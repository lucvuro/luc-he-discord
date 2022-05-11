import requests
import html
from bs4 import BeautifulSoup
import datetime
list12chd = {
    "aries":{
        "id": 1,
        "name": "Bạch Dương"
    },
    "taurus":{
        "id": 2,
        "name": "Kim Ngưu"
    },
    "gemini":{
        "id": 3,
        "name":"Song Tử"
    },
    "cancer":{
        "id": 4,
        "name": "Cự Giải"
    },
    "leo":{
        "id": 5,
        "name": "Sư Tử"
    },
    "virgo":{
        "id": 6,
        "name": "Xử Nữ"
    },
    "libra":{
        "id": 7,
        "name": "Thiên Bình"
    },
    "scorpius":{
        "id": 8,
        "name": "Thiên Yết"
    },
    "sagittarius":{
        "id": 9,
        "name": "Nhân Mã"
    },
    "capricorn":{
        "id": 10,
        "name": "Ma Kết"
    },
    "aquarius":{
        "id": 11,
        "name": "Bảo Bình"
    },
    "pisces":{
        "id": 12,
        "name": "Song Ngư"
    }
}
class BanDoSao:
    def __init__(self,name,gioitinh,ngaysinh,giosinh):
        self.name = name
        self.gioitinh = gioitinh
        self.ngaysinh = ngaysinh
        self.giosinh = giosinh
    def check_type(self):
        check_ngaysinh = BanDoSao.tachngaysinh(self.ngaysinh)
        check_giosinh = BanDoSao.chuyen_gio_sinh(self.giosinh)
        check_gt = BanDoSao.check_gioitinh(self.gioitinh)
        if check_ngaysinh == False or check_giosinh == False or check_gt == False:
            return False
        return True
    def check_gioitinh(gioitinh):
        strr = gioitinh.split(" ")
        if len(strr) == 1:
            if strr[0].lower() in ['nam','nữ']:
                return True
        return False
    def tachngaysinh(ngaysinh):
        # ngay = ngaysinh[0:ngaysinh.index("/")]
        # thang = ngaysinh[ngaysinh.index("/")+1:ngaysinh.rindex("/")]
        # nam = ngaysinh[ngaysinh.rindex("/")+1:]
        # return ngay,thang,nam
        format = "%d/%m/%Y"
        try:
            date = datetime.datetime.strptime(ngaysinh, format)
            return date.day, date.month,date.year
        except ValueError:
            return False
    def chuyen_gio_sinh(giosinh):
        # gio = giosinh[0:giosinh.index(":")]
        # phut = giosinh[giosinh.index(":")+1:]
        format = "%H:%M"
        try:
            date = datetime.datetime.strptime(giosinh, format)
            gio = date.hour
            phut = date.minute
            if int(gio) >= 0 and int(gio) < 12 or int(gio) == 24:
                if int(gio) == 0 or int(gio)==24:
                    gio = "12"
                return gio,phut,"AM"
            elif int(gio) >= 12 and int(gio) <24:
                gio = str(int(gio)-12)
                if int(gio) == 0:
                    gio = "12"
                if len(gio) < 2:
                    gio = "0" + gio
                return gio,phut,"PM"
        except ValueError:
            return False
    def tach_chuoi_lay_chu(text):
        for i in  range(len(text)):
            if text[i].isnumeric():
                return text[:i-1]
    def ten_tieng_anh_chd(tenchd):
        list_keys = list(list12chd.keys())
        for name in list_keys:
            if tenchd == list12chd[name]['name']:
                return name
    def get_chd(key,attribute):
        return list12chd[f'{key}'][f'{attribute}']
    def taonha(chd):
        chd_eng = BanDoSao.ten_tieng_anh_chd(chd)
        list_keys = list(list12chd.keys())
        chd_pos = BanDoSao.get_chd(chd_eng,'id') - 1
        nha = []
        for i in range(chd_pos,len(list_keys)):
            nha.append(list_keys[i])
        for i in range(chd_pos):
            nha.append(list_keys[i])
        return nha
    def taobandosao(self):
        # url = "http://astroviet.com/ban-do-sao/
        # tach ngay sinh
        ngay,thang,nam = BanDoSao.tachngaysinh(self.ngaysinh)
        gio,phut,amorpm = BanDoSao.chuyen_gio_sinh(self.giosinh)
        try:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                # Requests sorts cookies= alphabetically
                # 'Cookie': '_ga=GA1.2.1542659006.1650259077; _gid=GA1.2.487034402.1650433145; PHPSESSID=m0oumb9689j515uq2a8on11a0o; _gat_gtag_UA_78870804_12=1',
                'Origin': 'http://astroviet.com',
                'Referer': 'http://astroviet.com/ban-do-sao/',
                # 'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
            }

            data = {
                'natal_name': f'{self.name}',
                'natal_gender': f'{self.gioitinh}',
                'address': 'Thành phố Hồ Chí Minh',
                'lat': '',
                'lon': '',
                'timezone': '-7',
                'natal_day': f'{ngay}',
                'natal_month': f'{thang}',
                'natal_year': f'{nam}',
                'natal_hour': f'{gio}',
                'natal_minute': f'{phut}',
                'amorpm': f'{amorpm}',
                'long_deg': '',
                'long_min': '',
                'lat_min': '',
                'lat_deg': '',
                'ew': '',
                'ns': '',
                'natal_submitted': '0',
            }
            response = requests.post('http://astroviet.com/ban-do-sao/',headers=headers, data=data, verify=False)
            soup = BeautifulSoup(response.content, 'html5lib')
            article_4816 = soup.find_all("article", {"id": "page-4816"})
            link_image = "http://astroviet.com"+html.unescape(article_4816[0].find("img")['src'][2:]).replace(" ","%20")
            tbody_list = article_4816[0].find_all("tbody")
            list_tr_tbody1 = tbody_list[0].find_all("tr")
            cungmattroi = BanDoSao.tach_chuoi_lay_chu(list_tr_tbody1[1].find_all("td")[1].text)
            cungmattrang = BanDoSao.tach_chuoi_lay_chu(list_tr_tbody1[2].find_all("td")[1].text)
            list_tr_tbody2 = tbody_list[1].find_all("tr")
            cungmoc = BanDoSao.tach_chuoi_lay_chu(list_tr_tbody2[1].find_all("td")[1].text)
            nha = BanDoSao.taonha(cungmoc)
            return link_image,cungmattroi,cungmattrang,cungmoc,nha
        except:
            pass
if __name__ == '__main__':
    BanDoSao.taonha("Nhân Mã")