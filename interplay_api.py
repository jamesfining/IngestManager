from zeep import Client, xsd  # python soap client :)
from config import INTERPLAY_PASSWORD, INTERPLAY_USERNAME, INTERPLAY_ASSET_WSDL, INTERPLAY_JOB_WSDL, INTERPLAY_ARCHIVE_WSDL, INTERPLAY_PATHS, INTERPLAY_MOB_URI, INTERPLAY_ARCHIVE_PROFILE
from datetime import datetime, timedelta
from build_all_tables import FilesDropped, db_session
from time import sleep

# make some soap clients
asset_client = Client(wsdl=INTERPLAY_ASSET_WSDL)
job_client = Client(wsdl=INTERPLAY_JOB_WSDL)
archive_client = Client(wsdl=INTERPLAY_ARCHIVE_WSDL)


def make_asset_object(asset):  # turns the raw xml python dict into more usable dict
    temp_asset = {}
    for attribute in asset['Attributes']['Attribute']:  # convert strings to usable types
        if attribute['Name'] == 'Modified Date' or attribute['Name'] == 'Creation Date':
            temp_asset[attribute['Name']] = datetime.strptime(attribute['_value_1'], '%Y-%m-%dT%H:%M:%S.%f%z')
        elif attribute['Name'] == 'Duration' or attribute['Name'] == 'Start' or attribute['Name'] == 'End':
            t = datetime.strptime(attribute['_value_1'], '%H;%M;%S;%f')
            temp_asset[attribute['Name']] = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second).total_seconds()
        else:
            temp_asset[attribute['Name']] = attribute['_value_1']
    return temp_asset


def get_children(path):  # recursively finds master clips in folders and subfolders
    assets_to_return = []
    user_creds = asset_client.get_element(
        '{http://avid.com/interplay/ws/assets/types}UserCredentials')  # gets UserCredentials object
    header_value = user_creds(Username=INTERPLAY_USERNAME,
                              Password=INTERPLAY_PASSWORD)  # makes UserCredentials object with our username and password
    rval = asset_client.service.GetChildren(
        _soapheaders=[header_value],  # creds
        InterplayURI=path,
        IncludeFolders='true',
        IncludeFiles='true',
        IncludeMOBs='true'
    )
    if rval['Results'] is not None:
        for asset in rval['Results']['AssetDescription']:
            temp_asset = make_asset_object(asset)
            if temp_asset['Type'] == 'masterclip' and temp_asset['Media Status'] == 'online':  # only grab masterclips
                assets_to_return.append(temp_asset)
            elif temp_asset['Type'] == 'folder':
                assets_to_return = assets_to_return + get_children(asset['InterplayURI'])
    return assets_to_return


def get_assets():  # SHOW ME WHAT YOU GOT!
    user_creds = asset_client.get_element('{http://avid.com/interplay/ws/assets/types}UserCredentials')  # gets UserCredentials object
    header_value = user_creds(Username=INTERPLAY_USERNAME, Password=INTERPLAY_PASSWORD)  # makes UserCredentials object with our username and password
    assets = []
    for path in INTERPLAY_PATHS:  # loops through the paths we want to look at
        assets += get_children(path)
    return assets


def archive_asset(asset):
    if '/ING1' in asset.file_path:  # where did the asset come from
        interplay_mob_uri = INTERPLAY_MOB_URI[0]
        interplay_archive_profile = INTERPLAY_ARCHIVE_PROFILE[0]  # set the archive profile to NOCA
    else:
        interplay_mob_uri = INTERPLAY_MOB_URI[1]
        interplay_archive_profile = INTERPLAY_ARCHIVE_PROFILE[1]  # set the archive profile to NOCB
    user_creds = job_client.get_element(
        '{http://avid.com/interplay/ws/assets/types}UserCredentials')  # gets UserCredentials object
    header_value = user_creds(Username=INTERPLAY_USERNAME,
                              Password=INTERPLAY_PASSWORD)  # makes UserCredentials object with our username and password
    # submit for archive
    status = job_client.service.SubmitJobUsingProfile(
        _soapheaders=[header_value],
        InterplayURI=interplay_mob_uri + asset.mob_id,
        Service='com.avid.dms.archive',
        Profile=interplay_archive_profile
    )
    if status['JobURI'] is not None:  # the job was successfully submitted
        asset.date_archived = datetime.utcnow()
        asset.job_uri = status['JobURI']
        db_session.commit()
        sleep(60)  # give the archive engine a minute to process the request
        if check_job_status(asset.job_uri)['Status'] == 'Error':  # could not archive (probably deleted)
            delete_job(asset)  # cancel the job to clear the queue
            return -1  # something went wrong
        return 1  # asset will be archived
    else:  # something went wrong
        return -1


def submit_for_archive(asset):  # Archive this please
    if '/ING1' in asset.file_path:  # where did the asset come from
        interplay_mob_uri = INTERPLAY_MOB_URI[0]
        interplay_archive_profile = INTERPLAY_ARCHIVE_PROFILE[0]  # set the archive profile to NOCA
    else:
        interplay_mob_uri = INTERPLAY_MOB_URI[1]
        interplay_archive_profile = INTERPLAY_ARCHIVE_PROFILE[1]  # set the archive profile to NOCB

    # does the archive service know about this object?
    user_creds = archive_client.get_element('{http://avid.com/interplay/ws/assets/types}UserCredentials')  # gets UserCredentials object
    header_value = user_creds(Username=INTERPLAY_USERNAME, Password=INTERPLAY_PASSWORD)  # makes UserCredentials object with our username and password
    status = archive_client.service.GetFileDetails(
        _soapheaders=[header_value],
        InterplayURIs=[interplay_mob_uri + asset.mob_id]
    )

    if status['Errors'] is None:  # asset has already been archived
        fully_archived = True
        for file in status['Results']['FileLocationDetails'][0]['FileLocations']['FileLocation']:
            if file['Status'] == 'Offline':
                fully_archived = False
        if fully_archived:
            return 0
    return archive_asset(asset)# asset has not been archived


def check_job_status(asset_job_uri):  # How You Doin'?
    user_creds = job_client.get_element('{http://avid.com/interplay/ws/assets/types}UserCredentials')
    header_value = user_creds(Username=INTERPLAY_USERNAME, Password=INTERPLAY_PASSWORD)
    status = job_client.service.GetJobStatus(
        _soapheaders=[header_value],
        JobURIs=[asset_job_uri]
    )
    print('Job Status ' + status['JobStatusTypes']['JobStatus'][0]['Status'])
    return status['JobStatusTypes']['JobStatus'][0]


def delete_job(asset):  # Hold the pickles
    user_creds = job_client.get_element('{http://avid.com/interplay/ws/assets/types}UserCredentials')
    header_value = user_creds(Username=INTERPLAY_USERNAME, Password=INTERPLAY_PASSWORD)
    status = job_client.service.DeleteJobs(
        _soapheaders=[header_value],
        JobURIs=[asset.job_uri]
    )


def cancel_job_if_pending(asset):
    if asset is None:
        return
    job_status = check_job_status(asset.job_uri)
    if job_status['Status'] == "Processing" and job_status['PercentComplete'] <= 1:
        user_creds = job_client.get_element('{http://avid.com/interplay/ws/assets/types}UserCredentials')
        header_value = user_creds(Username=INTERPLAY_USERNAME, Password=INTERPLAY_PASSWORD)
        status = job_client.service.CancelJobs(
            _soapheaders=[header_value],
            JobURIs=[asset.job_uri]
        )
        asset.job_uri = None
        asset.date_archived = None
        print("Canceled archive of " + asset.mob_id)

