import os
import swiftclient
from flask import Flask, request, render_template,make_response
import pyDes
#import gnupg
app = Flask(__name__)

# Read port selected by the cloud for our application
PORT = int(os.getenv('PORT', 8000))
# Change current directory to avoid exposure of control files
k = pyDes.des(b"DESCRYPT", pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
#gpg = gnupg.GPG()
#input_data = gpg.gen_key_input(key_type="RSA", key_length=1024, passphrase='password')
#key = gpg.gen_key_input(input_data)
auth_url = "https://identity.open.softlayer.com/v3"
password = "N[/]=X2g~1K1Us0Y"
project_id = "dc2d35de010142e5a53ae9344b388c2e"
user_id = "14b395b13e4b4d9baa0a25e4f281939c"
region_name = "dallas"
conn = swiftclient.Connection(key=password,	authurl=auth_url, auth_version='3', os_options={"project_id": project_id, "user_id": user_id, "region_name": region_name})
cont_name = "new_container"
conn.put_container(cont_name)


@app.route("/")
def main():
    return render_template('index.html')

@app.route("/upload", methods=['GET', 'POST'])
def upload_file():
    if not file:
        return "No file"
    else:
        f = request.files['file']
        file_name = f.filename
        file_content = f.read()
        file_length = int(len(file_content))
        enc = k.encrypt(file_content)
        #status = gpg.encrypt(file_content)
        data = conn.get_account()[0]
        size_cont = int(data['x-account-bytes-used'])
        total_size = file_length + size_cont
        if file_length < 1000000 | total_size < 10000000:
            conn.put_object(cont_name, file_name, contents=enc, content_type='text/plain')
            return 'File Uploaded'

        else:
            return 'Size exceeded. Please try again.'

@app.route("/download", methods=['GET', 'POST'])
def download_file():
    if not file:
        return "No file"
    else:
        f = request.args.get('dwnfile', '')
        obj_tuple = conn.get_object(cont_name, f)
        file_open = make_response(k.decrypt(obj_tuple[1]))
        file_open.headers["Content-Disposition"] = "attachment; filename="+f
        #file_contents = k.decrypt(filebytes)
        #file_open = open('my.txt', 'w')
        #file_open.write(filebytes)
    return file_open

@app.route("/delete", methods=['GET', 'POST'])
def delete_file():
    if not file:
        return "No file"
    else:
      #f = request.form['delfile']
      f = request.args.get('delfile', '')
      if not f:
       return 'No such file is available'
      else:
       conn.delete_object(cont_name, f)
       return 'File Deleted'

@app.route("/list1", methods=['GET', 'POST'])
def list_file():
    lists = ''
    #for container in conn.get_account()[1]:
        #print conn.get_account()
    for data in conn.get_container(cont_name)[1]:
        lists = lists + 'object: {0}\t size: {1}\t date: {2}'.format(data['name'], data['bytes'], data['last_modified']) + "<br/>"
    return lists


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT, debug=True)