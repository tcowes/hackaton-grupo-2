import json
import base64
try:
    import settings
except:
    import os
    import sys
    path = os.path.abspath('.')
    sys.path.insert(1, path)
from settings import settings


class Security():

    def __init__(self) -> None:
        self._api_token = settings.API_TOKEN
        self._raw_str = self.decode_data()

    def obtain_ip_address(self, server_name):
        content_ = json.loads(self._raw_str)
        return content_[0][server_name]

    @classmethod
    def decode_data(cls) -> str:
        data_decoded = base64.b85decode(DATA.replace(b"\n", b""))
        return data_decoded.decode("UTF-8")


DATA = b"""
TYDlyK_WUJA~7>KE-^VbE-^AWE-^JXA}k;xLqRekIv^r3GdM0WIX5mbH#IIXI5{FLAR<RXB03-<F)%b
PGBh|YF*h<UG9oM>B1b|pB03-<GB7qSF*rFcF)=wVIWr<GAR<*$B03-<F*Y|YF*h<UGBPWF)%bDEFd
CPQ!*ktAR;m_HZCzZIW93bGcGbTA}k;xQ%52?AR;j~H!e9jE;cnTF*P(IEFdCIOd>iUA~7~ME;lhQHZ
CzWG$Je@B1A<ZIv^r6HZCzRF)lJPFfKMCEFdC8MKU5fAR;j}IW9OkE;%XF*Y$GEFdC8MKdBgAR;t2E
-^4ME;2ASE-^GWA}k;xL`5xBWpi{fB03-<GB7qSI593VH7qXA}k;xZE161bZ;U$AR;j~I4(9ZE;lnS
I5{FLAR=pFYH1=mAR;j^G%hqUE-^7OE-^DSB7I!
"""
