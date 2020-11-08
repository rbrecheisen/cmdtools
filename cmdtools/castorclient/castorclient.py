from cmdtools.castorclient.export import CastorExportClient
from cmdtools.castorclient.importandupdate import CastorImportAndUpdateClient


class CastorClient(CastorExportClient, CastorImportAndUpdateClient):

    def __init__(self):
        super(CastorClient, self).__init__()
