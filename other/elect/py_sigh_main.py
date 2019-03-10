from flask import Flask,request,render_template,url_for,abort,redirect,json,jsonify

app = Flask(__name__)


@app.route("/")
def home():
    print(url_for('home'))
    print(url_for('sigh'))
    print(url_for("user_info"))
    return 'Index Page'
@app.route("/sigh")
def sigh():
    args=request.args
    for key in args.keys():
        print(key,":",args[key])
    flag = True
    for key in ["id","name","phone"]:
        if not key in args.keys():
            flag = False
    if flag == True:
        print("字段已找到")
        id = args["id"]
        name = args["name"]
        phone = args["phone"]
        return redirect(url_for("user_info",id=id,name=name,phone=phone))
    """A test client for the app."""
    ip = request.remote_addr
    print(ip)
    return render_template("sigh.html")
@app.route("/user")
def user_info():
    # args = request.args
    # flag = True
    # for key in ["id","name","phone"]:
    #     if not key in args.keys():
    #         flag = False
    # if flag == True:
    #     id = args["id"]
    #     name = args["name"]
    #     phone = args["phone"]
    # else:
    #     abort(404)
    return render_template("info.html")  # ,id=id,name=name,phone=phone
@app.route("/api/login",methods=["POST","GET"])
def api_login():
    #data = request.form["id"]
    #print("data:",data)
    # data = json.loads(data)
    # callback = data["callback"]
    id = request.form["id"]
    name = request.form["name"]
    phone = request.form["phone"]
    print(id)
    print(name)
    print(phone)
    return jsonify({"id":id,"name":name,"phone":phone})
    # args = request.args
    # #print(data)
    # callback = args["callback"]
    # id = args["id"]
    # name = args["name"]
    # phone = args["phone"]
    # print(id)
    # print(name)
    # print(phone)
    # return callback+jsonify({"id":id,"name":name,"phone":phone})



@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"),404

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=80,debug=True)
