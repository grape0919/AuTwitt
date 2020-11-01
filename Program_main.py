import sys
from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog, QMessageBox,QLabel
from view.main import Ui_MainWindow
from nohand.blogInfo import selProp
from nohand.blogInfo import ApiProp
from nohand.noHandBlogger import ApiBlogger, SeleniumBlogger

import static.staticValues as staticValues

class WindowClass(Ui_MainWindow) :

    running = False
    login = False

    def __init__(self) :
        super(WindowClass, self).__init__()
        self.setupUi(self)
        
        self.button_file.clicked.connect(self.showFileDialog)
        
        self.button_getToken.clicked.connect(self.getTokenUrl)

        self.button_write.clicked.connect(self.writeArticle)
        self.button_write.setEnabled(False)

        # self.prop = selProp()
        # self.edit_url.setText(self.prop.url)
        # self.edit_id.setText(self.prop.id)
        # self.edit_passwd.setText(self.prop.passwd)
        self.prop = ApiProp()
        self.edit_key.setText(self.prop.app_id)
        self.edit_secret_key.setText(self.prop.scrt_key)
        # self.edit_token.setText(self.prop.token)

        # self.blogger = SeleniumBlogger(self.label_countdown)
        self.blogger = ApiBlogger(self.label_countdown)

    def getTokenUrl(self):
        self.prop.app_id = self.edit_key.text()
        self.prop.scrt_key = self.edit_secret_key.text()
        self.prop.save()
        
        self.blogger.setProp(self.prop)

        keyUrl = self.blogger.getKeyUrl()
        
        if(keyUrl):
            text, ok = QInputDialog.getText(self, "인증키", "<p>아래 링크에 접속하여 인증 코드를 입력해주세요.\
                </p><p><a href='"+keyUrl+"'>인증 링크</a></p><p></p>")
            if ok: 
                success = self.blogger.getToken(text)
                if success :
                    self.button_write.setStyleSheet(staticValues.blueButtonStyleSheet)
                    self.button_write.setEnabled(True)

                    self.button_getToken.setEnabled(False)
                    self.button_getToken.setStyleSheet(staticValues.grayButtonStyleSheet)

                    self.login = True 
                else :

                    self.login = False
                    QMessageBox.warning(self, "인증코드", "인증코드가 잘못되었습니다. 다시 확인해주세요.")

        else:
            QMessageBox.information(self, "인증키", "<p>API_KEY, SECRET_KEY를 확인해주세요.</p>\
                </br><p>API_KEY는 <a href='http://hleecaster.com/twitter-api-developer/'>여기</a> 블로그를 참고하여 생성하세요.</p>")



    def showFileDialog(self):
        print("Clicked button")
        fname = QFileDialog.getOpenFileName(self, 'Open excel for paragraph', 'Desktop',
                                            "Excel (*.xls *.xlsx)")
        if fname[0]:
            self._filePath = fname[0]
            self.edit_filePath.setText(fname[0])

    def writeArticle(self):
        print("Clicked write button")

        if(self.running == False):
            if(self.edit_filePath.text() == None or self.edit_filePath.text() == ""):
                QMessageBox.about(self, "Warning", "문단 파일을 먼저 선택하세요.")
                return
                
            if(self.edit_period.text() == '' or int(self.edit_period.text()) < 5 ):
                QMessageBox.about(self, "Warning", "게시 주기는 최소 5분 이상 설정할 수 있습니다..")
                return
                
            QMessageBox.about(self, "자동 게시 시작", "자동 글쓰기를 시작합니다.")
            self.button_write.setText("자동 등록 중")
            self.button_write.setStyleSheet(staticValues.redButtonStyleSheet)

            self.blogger.setDate(self.dateTime_upload.dateTime() ,int(self.edit_period.text()))

            self.running = True

            self.blogger.readExcelFile(self.edit_filePath.text())
            suc = self.blogger.postArticle()
            
            if(suc is not None and not suc[0]):
                QMessageBox.about(self, "경고", suc[1])
                self.button_write.setText("자동 등록 시작")
                self.button_write.setStyleSheet(staticValues.blueButtonStyleSheet)
                self.running = False
                self.blogger.running = False

        else:
            QMessageBox.about(self, "자동 포스팅 정지", "자동 포스팅을 정지합니다.")
            self.button_write.setText("자동 등록 시작")
            self.button_write.setStyleSheet(staticValues.blueButtonStyleSheet)
            self.running = False
            self.blogger.running = False

    def closeEvent(self, event):
       self.running = False
       self.blogger.running = False
       if(self.blogger.postThread is not None):
           self.blogger.postThread.join()
           
       event.accept()
        


if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv) 

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass()
    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
