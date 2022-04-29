from flask import Blueprint, render_template, request, flash, jsonify
from . import dynamo_db
import json, os, boto3
from werkzeug.utils import secure_filename

access_key_id = "ASIA23OAS5CFJTGIDDNM"
secret_access_key = "SmTom0yPWUT2VhW3hpZSjGQs7vQXAKuYeW1dQ19y"
session_token = "FwoGZXIvYXdzEEYaDLD3EHMUIkmxTZdzdSLNASigJUllY3E+jXg4qALLsRq5CwiLk5SXwFpReLLjlcKxzD9gd7CUruZbHJ0FEYYq3eNzCLsMTGqtnIbjeqK+r6IEmig0ozvlKyEIcER3KCcfMHjXXBYykqEELjccyVmF6RMd66vNpNTof6fVt+Vkni5q09/f4eOoQ+pBD86beva82cBD3/1+T+oMznsEyi+k0ln5lPy6HUa7YMmoD0ausL1VtU5AfY6yP8B/8ebTpfupIKy0WR7RMRyLrEF41KW+BYZx2A6EJq3NEF0Ji5Io6sCvkwYyLc+PxvCuVFBvWWOi1EbybFY9VlWNSbR6LAttqgVQggyHibrkQJo7dD32eCXigw=="

s3 = boto3.client('s3',
            region_name="us-east-1",
            aws_access_key_id = access_key_id,
            aws_secret_access_key = secret_access_key,
            aws_session_token = session_token
)

bucket_name = "elasticbeanstalk-us-east-1-746117589130"

# this file is a blueprint of our app 
# (it contains all the routes)
views = Blueprint('views', __name__)


# to check when a folder was last updated
def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))


# posts image to S3 and image details to DB
def post_image(email, filename, visibility):
    check = filename.split('.')
    type = "image/" + check[1]                  
    s3.upload_file(
        Bucket = bucket_name,
        Filename=filename,
        Key = filename,
        ExtraArgs={'ContentType': type, 'ACL': "public-read"}
    )
    os.remove(filename)
    dynamo_db.create_user_image(email, filename, visibility)


# defining routes
@views.route('/home/<user>', methods=['GET', 'POST'])
def home(user):
    email = str(user)
    current_user = dynamo_db.get_user(email)

    if (request.method == 'POST'):

        if ("usr-img" in request.files.keys()):         
            usr_img = request.files["usr-img"]
            if not usr_img:
                flash('No image was uploaded!', category='error')
            else:
                filename = secure_filename(usr_img.filename)
                check = filename.split('.')
                if (check[1] != "png" and check[1] != "jpeg"
                    and check[1] != "jpg"):
                    flash('Only images with extensions: .png, .jpeg, .jpg are allowed!', category='error')
                else:
                    if ("public" in request.form.keys()):
                        vis = "public"
                    else:
                        vis = "private"

                    usr_img.save(filename)
                    post_image(email, filename, vis)
                    flash('Image uploaded!', category='success')
                    all_images = dynamo_db.get_all_images()
                    all_notes = dynamo_db.get_all_notes()
                    return render_template("home.html", user=current_user, images=all_images, notes=all_notes, last_updated=dir_last_updated('website/static'))       
        else:
            note = request.form.get('note') 
            if (len(note) < 1):
                flash('Notes must be at least 1 character long!', category='error')
            else:
                
                if ("public" in request.form.keys()):
                    vis = "public"
                else:
                    vis = "private"

                dynamo_db.create_user_note(email, note, vis)
                all_notes = dynamo_db.get_all_notes()
                all_images = dynamo_db.get_all_images()
                return render_template("home.html", user=current_user, notes=all_notes, images=all_images, last_updated=dir_last_updated('website/static'))

    all_notes = dynamo_db.get_all_notes()
    all_images = dynamo_db.get_all_images()
    return render_template("home.html", user=current_user, notes=all_notes, images=all_images, last_updated=dir_last_updated('website/static'))


@views.route('/share/<email>/<id>', methods=['GET', 'POST'])
def share(email, id):
    mail = str(email)
    mail1 = mail.split("@")[0]
    mail2 = mail.split("@")[1]
    id = str(id)
    check = id[0:4]
    if (check == "note"):
        note = dynamo_db.get_note(email, id)
        return render_template("share.html", email1=mail1, email2=mail2, note=note, last_updated=dir_last_updated('website/static'))
    else:
        image = dynamo_db.get_image(email, id)
        return render_template("share.html", email1=mail1, email2=mail2, image=image, last_updated=dir_last_updated('website/static'))


@views.route('/delete-note', methods=['POST'])
def delete_note():
    # making the string sent from index.js
    # into a py dictionary
    note = json.loads(request.data.decode('utf-8'))
    # accessing the id
    s = note['noteId']
    email = s[0:s.index("note")]
    id = s[len(s)-1]
    # deleting note
    dynamo_db.delete_user_note(email, id)
    # returning empty response since 
    # it is a POST method
    return jsonify({})


@views.route('/delete-image', methods=['POST'])
def delete_image():
    url = json.loads(request.data.decode('utf-8'))
    email = url['email']
    name = url['name']
    # deleting image
    dynamo_db.delete_user_image(email, name)
    return jsonify({})
    

