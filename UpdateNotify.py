# pip install PyGithub if not already installed PyGithub.
from github import Github
import datetime
import sys
import os
import smtplib
from email.mime.multipart import  MIMEMultipart
from email.mime.text import MIMEText

import last_commit
#================== Configrations ==========================#
ACCESS_TOKEN="<GitHubのアクセストークン> "

mailing_list = [
    "kojo@wolfssl.com",
    "shingo@wolfssl.com"
    # "hide@wolfssl.com",
    # "tak@wolfssl.com"
]

MAIL_ADDRESS = "<Gmail のアドレス> "
MAIL_PASSWORD = "<Gmail のアプリケーションパスワード>" # ログインパスワードではない
#===========================================================#


# Set up 
def Setup():
    print("Called Setup!!")


def main():
    g = Github(ACCESS_TOKEN)
    repo = g.get_repo("wolfssl/documentation")

    # Check whether the LAST_COMMIT_SHA is None or not.
    try:
        Last_commit_sha = last_commit.LAST_COMMIT_SHA
    except:
        Setup()
        sys.exit(1)


    # Get the object of Last commit
    Last_commit = repo.get_commit(Last_commit_sha)

    Last_updated_datetime = Last_commit.commit.committer.date

    # Get the newly updated commits.
    new_commits = repo.get_commits(since=(Last_updated_datetime+datetime.timedelta(minutes=1)) )

    print("Num of New commits", new_commits.totalCount)

    # Check if the last commit is not out of date.
    if new_commits.totalCount == 0:
        print("Not Out of Date!")
        sys.exit(2)


    # Check Whether the Contents is updated or not.
    Notification_list = []

    for commit in new_commits:
        # Marge された時のコミットだけを見る。 （committerのcommitと重複してるから）
        if "Merge pull request" in commit.commit.message:

            Notify=False 
            for file in commit.files:
                # print(file.filename)
                if "src-ja" not in file.filename \
                            and "header-ja" not in file.filename \
                            and ".md" in file.filename:
                    Notify=True
                
            if Notify==True:
                Notification_list.append(commit)
                # print(file.filename, commit.commit.author.name, commit.commit.committer.date, commit.commit.html_url)
        

    
    # If there is not Updated Contents
    if len(Notification_list) == 0:
        print("Newly Merged but Not updated Contents")
        
 
        
    else:   # Updated Contents Exist!
        print("Updated Contents Exist!")
        print("Num of Updated Contents: ", len(Notification_list))
        
        # Do Notification
        for commit in reversed(Notification_list):
            print(commit.commit.committer.date)
            notifier = Notifier(commit,)
            notifier.gen_msg()

            for to_addr in mailing_list:

                notifier.Sendmail(to_addr)


    # Set the Newest Commit to LAST_COMMIT_SHA in last_commit.py
    with open('last_commit.py', mode = "w") as f:
        f.write(f'LAST_COMMIT_SHA = \"{new_commits[0].commit.sha}\"')



class Notifier():

    def __init__(self, commit, msg=""):
        self.commit = commit
        self.msg = msg

        self.updated_files = []

        for file in commit.files:
            self.updated_files.append(file.filename)


    def get_msg(self):
        return self.msg
    
    def gen_msg(self):
        msg = ""
        msg += f"[Date]         {self.commit.commit.committer.date}\n"
        msg += f"[Merged by]    {self.commit.commit.author.name}\n"
        msg += f"[Commit Message]\n"
        msg += f"{self.commit.commit.message}\n"
        
        msg += f"[Changed Files]\n\n"
        for filename in self.updated_files:
            msg += f"{filename}\n"
        msg += "\n"
        msg += f"[URL]  {self.commit.commit.html_url}\n"

        
        self.msg = msg


    def Sendmail(self, to_addr="shingo@wolfssl.com"):
        smtp_server = "smtp.gmail.com"
        port = 587

        server = smtplib.SMTP(smtp_server, port)
        server.starttls()

        server.login(MAIL_ADDRESS, MAIL_PASSWORD)

        message = MIMEMultipart()

        message["Subject"] = "Documentation Updated!"
        message["From"] = MAIL_ADDRESS
        message["To"] = to_addr

        text = MIMEText(self.get_msg())

        message.attach(text)

        server.send_message(message)

        server.quit()

    def SendLINE():
        pass

    def SendSlack():
        pass
    
if __name__ == '__main__':
    main()
