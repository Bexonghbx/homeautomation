"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file creates your application.
"""

# from crypt import methods
import site 

from app import app, Config,  mongo, Mqtt
from flask import escape, render_template, request, jsonify, send_file, redirect, make_response, send_from_directory 
from json import dumps, loads 
from werkzeug.utils import secure_filename
from datetime import datetime,timedelta, timezone
from os import getcwd
from os.path import join, exists
from time import time, ctime
from math import floor
 



#####################################
#   Routing for your application    #
#####################################


# 1. CREATE ROUTE FOR '/api/set/combination'
@app.route('/api/set/combination', methods=['POST']) 
def set_passcode():   
    '''Returns number which represents the amount of time a specific LED was turned on'''
    if request.method == "POST":
        try:
            form =  request.form

            newCode = escape(form.get("passcode"))
            code = mongo.updatePasscode(newCode)
            if code:
                return jsonify({"status":"complete","data": "complete"})
            
        except Exception as e:
            print(f"set_passcode error: f{str(e)}")        
    return jsonify({"status":"failed","data": "failed"})
    
# 2. CREATE ROUTE FOR '/api/check/combination'
@app.route('/api/check/combination', methods=['POST']) 
def check_passcode():   
    '''Returns number which represents the amount of time a specific LED was turned on'''
    
    if request.method == "POST":
        try:
            data = request.form

            Code = data.get("passcode")
            passcode = mongo.checkPasscode(Code)
            print("Passcode ",passcode)
            if passcode:
                return jsonify({"status":"complete","data": "complete"})
            
        except Exception as e:
            print(f"check_passcode error: f{str(e)}")        
    return jsonify({"status":"failed","data": "failed"})

# 3. CREATE ROUTE FOR '/api/update'
@app.route('/api/update', methods=['POST']) 
def update_radar():   
    '''Returns number which represents the amount of time a specific LED was turned on'''
    if request.method == "POST":
        try:
            data =  request.json
            data["timestamp"] = datetime.now()

            radar = json.dumps(data)
            passcode = mongo.addUpdate(radar)
            if passcode:
                return jsonify({"status":"complete","data": "complete"})
            
        except Exception as e:
            print(f"update_radar error: f{str(e)}")        
    return jsonify({"status":"failed","data": "failed"})


   
# 4. CREATE ROUTE FOR '/api/reserve/<start>/<end>'
@app.route('/api/reserve/<start>/<end>', methods=['GET']) 
def get_reserve(start,end):   
   
    if request.method == "GET": 
        '''Add your code here to complete this route'''
        try:
            st = escape(start)
            e  = escape(end)
            reserve = mongo.getAllInRange(st,e)
            if reserve:
                return jsonify({"status":"found","data": reserve})
            
        except Exception as e:
            print(f"getAllInRange error: f{str(e)}")

    # FILE DATA NOT EXIST
    return jsonify({"status":"not found","data":0})

# 5. CREATE ROUTE FOR '/api/avg/<start>/<end>'
@app.route('/api/avg/<start>/<end>', methods=['GET']) 
def get_reserve_a(start,end):   
   
    if request.method == "GET": 
        '''Add your code here to complete this route'''
        try:
            st = escape(start)
            e  = escape(end)
            rAVG = mongo.reserveAVG(st,e)
            if rAVG:
                return jsonify({"status":"found","data": rAVG})
            
        except Exception as e:
            print(f"get_reserve_a error: f{str(e)}")

    # FILE DATA NOT EXIST
    return jsonify({"status":"not found","data":0})



   






@app.route('/api/file/get/<filename>', methods=['GET']) 
def get_images(filename):   
    '''Returns requested file from uploads folder'''
   
    if request.method == "GET":
        directory   = join( getcwd(), Config.UPLOADS_FOLDER) 
        filePath    = join( getcwd(), Config.UPLOADS_FOLDER, filename) 

        # RETURN FILE IF IT EXISTS IN FOLDER
        if exists(filePath):        
            return send_from_directory(directory, filename)
        
        # FILE DOES NOT EXIST
        return jsonify({"status":"file not found"}), 404


@app.route('/api/file/upload',methods=["POST"])  
def upload():
    '''Saves a file to the uploads folder'''
    
    if request.method == "POST": 
        file     = request.files['file']
        filename = secure_filename(file.filename)
        file.save(join(getcwd(),Config.UPLOADS_FOLDER , filename))
        return jsonify({"status":"File upload successful", "filename":f"{filename}" })

 


###############################################################
# The functions below should be applicable to all Flask apps. #
###############################################################


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.errorhandler(405)
def page_not_found(error):
    """Custom 404 page."""    
    return jsonify({"status": 404}), 404



