# :: Weasley Project ::
- [Demo Video](https://user-images.githubusercontent.com/31269150/145545352-c82be4a1-e095-48ae-a37a-393adf8f69a0.mp4)
- 짧은 프로젝트 기간동안 개발에 집중해야하므로 디자인/기획 부분만 클론했습니다.
- 개발은 초기 세팅부터 전부 직접 구현했으며, 실제 사용할 수 있는 서비스 수준으로 개발한 것입니다.


## [팀 소개]
### Front-end
[Weasley - Frontend Repo](https://github.com/wecode-bootcamp-korea/27-1st-weasley-frontend)

### Back-end
😎 강태준 - 인가 데코레이터, 값 검증 Validator, 장바구니/구매 관련 뷰, 구독 관리 뷰(GET)<br/>
🍗 길동화 - 제품 뷰, 구독 관리 뷰(DELETE), 유저 관련 뷰(회원가입)<br/>
👻 염기욱 - 카테고리 뷰, 구독 관리 뷰(POST, PATCH)

### 개발 기간
2021.11.29 ~ 2021.12.10

## [기술 스택]
### 사용 기술
Django, Python, MySQL, jwt, bcrypt, AWS(EC2, RDS), Docker, Schdule, Git

### ERD
<img width="1018" alt="스크린샷 2021-12-04 14 50 46" src="https://user-images.githubusercontent.com/31269150/145546704-f63f872d-047a-4fb6-8eb8-344686afcfe3.png">

### Docker
0. install Docker on the server/computer you want to run this project
1. git clone https://github.com/wecode-bootcamp-korea/27-1st-weasley-backend.git 
2. run to build docker image -> docker build -f Dockerfile.web -t [your docker-hub name]/weasley:[tag] . / docker build -f Dockerfile.schedule -t [your docker-hub name]/weasley-schedule:[tag] . -> you have to build twice cause of background-scheduler
3. run to push on your docker hub -> docker push [your docker-hub name]/weasley:[tag] / docker push [your docker-hub name]/weasley-schedule:[tag]
4. request pull on server you want to make docker container -> docker run --name weasley -dp 8000:8000 [your docker-hub name]/weasley:[tag] / docker run --name weasley -d [your docker-hub name]/weasley-schedule:[tag]
5. you can see logs by -> docker logs -f weasley / docker logs -f weasley-schedlue
#### ENJOY! :)

## Reference
- [API Document](https://docs.google.com/spreadsheets/d/1VEnmoeMfSquz6PnfTI9717p0FvRqJzT_ZRAklIup-lY/edit?usp=sharing)
- 이 프로젝트는 [와이즐리 오픈워크](https://openwork.wiselycompany.com/) 사이트를 참조하여 학습목적으로 만들었습니다.
- 실무수준의 프로젝트이지만 학습용으로 만들었기 때문에 이 코드를 활용하여 이득을 취하거나 무단 배포할 경우 법적으로 문제될 수 있습니다.
