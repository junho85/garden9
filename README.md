# garden8
* 정원사들 시즌8 출석부입니다.
* slack #commit 채널에 올라온 메시지들을 수집해서 출석부를 작성합니다.
* [시즌8 출석부 바로가기 gogo](http://garden8.junho85.pe.kr/)
* [github](https://github.com/junho85/garden8)
* [wiki](https://github.com/junho85/garden8/wiki)

## project
start mongodb
```
docker start mymongo
```

activate virtual env
```
source venv/bin/activate
```

install packages
```
pip install -r requirements.txt
```

run server
```
python manage.py runserver
```

자세한 내용은 [docs](docs)의 내용을 참고합니다.

## 설정
기본 설정 경로는 `/config/attendance` 를 사용합니다.

환경변수 GARDEN_CONFIG_DIR 를 설정해 주면 해당 경로로 변경됩니다.

e.g.
```
GARDEN_CONFIG_DIR=./config/attendance python ./manage.py runserver 0.0.0.0:8000
```

## 참고
* [garden7 github](https://github.com/junho85/garden7)
* [garden6 github](https://github.com/junho85/garden6)
* [garden5 github](https://github.com/junho85/garden5)
* [garden4 github](https://github.com/junho85/garden4)