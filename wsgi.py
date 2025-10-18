from app.app import jarvis_deploy_website

app = jarvis_deploy_website()

if __name__ == "__main__":
    app.run()
    print("> Email service is up")
