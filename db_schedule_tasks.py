from build_all_tables import FilesDropped, db_session
from interplay_api import get_assets


def update_db():
    assets = get_assets()  # get the assets from Interplay

    for asset in assets:
        try:
            fd = FilesDropped(
                asset['MOB ID'],
                asset['Path'],
                asset['Duration'],
                asset['Creation Date'],
                asset['Modified Date'],
                asset['Display Name']
            )
            db_session.merge(fd)
            db_session.commit()
        # gotta catch 'em all
        except Exception as e:  # handle this exception more explicitly (its never been hit so Idk what to expect)
            print('Something went wrong in update_db ' + str(e))
            db_session.rollback()
