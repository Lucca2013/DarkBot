from flask import Blueprint, request, jsonify, render_template, current_app
import jwt
import os
import asyncio
from dotenv import load_dotenv
from bot.commands import send_embed, create_channel

load_dotenv()

routes_bp = Blueprint('routes', __name__)

@routes_bp.route('/get_server_info_by_jwt', methods=['GET'])
def get_server_info_by_jwt():
    token = request.args.get('token')
    
    if not token:
        return jsonify({"error": "No token provided"}), 400
    
    try:
        decoded_token = jwt.decode(token, os.getenv("JWT_KEY"), algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "The token has expired"}), 400
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 400
    
    subject = decoded_token["subject"]
    subject.pop("id", None)
    
    return jsonify(subject), 200

@routes_bp.route('/create_embed', methods=['POST'])
def create_embed():
    token = request.headers.get("Authorization")
    data = request.get_json(silent=True)
    
    secret = os.getenv("JWT_KEY")
    
    if not token:
        return jsonify({"error": "No authorization provided"}), 400
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        decoded_token = jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "The token has expired"}), 400
    except jwt.InvalidTokenError as e:
        print(f"JWT Exception details: {type(e).__name__} - {str(e)}")
        return jsonify({"error": f"Invalid token: {str(e)}"}), 400
    
    bot = current_app.bot
    
    try:
        async_send_embed = asyncio.run_coroutine_threadsafe(
            send_embed(
                bot,
                decoded_token["subject"]["id"],
                data.get("channel_id"),
                data.get("author"),
                data.get("title"),
                data.get("url"),
                data.get("color"),
                data.get("description"),
                data.get("image"),
                data.get("thumbnail"),
                data.get("footer")
            ),
            bot.loop
        )
        result = async_send_embed.result(timeout=5)
    except Exception as e:
        return jsonify({"error": f"Failed to execute: {str(e)}"}), 500
    
    if result is True:
        return jsonify({"status": "sent"}), 200
    
    return jsonify({"error": str(result)}), 400

@routes_bp.route('/create_ticket', methods=['POST'])
def create_ticket():
    token = request.headers.get("Authorization")
    data = request.get_json(silent=True)
    
    secret = os.getenv("JWT_KEY")
    
    if not token:
        return jsonify({"error": "No authorization provided"}), 400
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        decoded_token = jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "The token has expired"}), 400
    except jwt.InvalidTokenError as e:
        print(f"JWT Exception details: {type(e).__name__} - {str(e)}")
        return jsonify({"error": f"Invalid token: {str(e)}"}), 400
    
    bot = current_app.bot
    
    try:      
        if(data.get("create_text_channel")):
            async_create_channel = asyncio.run_coroutine_threadsafe(
                create_channel(
                    bot,
                    "ticket",
                    int(decoded_token["subject"]["id"])
                ),
                bot.loop
            )
            success, info = async_create_channel.result(timeout=5)
            
            if not success:
                return jsonify({"error": info}), 400
            
            channelId = info
            
            async_create_channel2 = asyncio.run_coroutine_threadsafe(
                create_channel(
                    bot,
                    "ticket_feedback",
                    int(decoded_token["subject"]["id"]),
                    adm_only=True
                ),
                bot.loop
            )
            success2, info2 = async_create_channel2.result(timeout=5)
            
            if not success2:
                return jsonify({"error": info2}), 400
            
            feedbackChannelId = info
        else:
            channelId = data.get("channel")
            feedbackChannelId = data.get("feedback_channel")
        
        footer = {"text": data.get("footer")}
                
        async_send_embed = asyncio.run_coroutine_threadsafe(
            send_embed(
                bot,
                decoded_token["subject"]["id"],
                channelId,
                data.get("author"),
                data.get("title"),
                color=data.get("color"),
                description=data.get("description"),
                footer=footer,
                options=data.get("options"),
                mention_role=data.get("role"),
                ticket_additionals={"feedback_channel": feedbackChannelId}
            ),
            bot.loop
        )
        result = async_send_embed.result(timeout=5)
    except Exception as e:
        print(e)
        return jsonify({"error": f"Failed to execute: {str(e)}"}), 500
    
    if result is True:
        return jsonify({"status": "sent"}), 200
    
    return jsonify({"error": str(result)}), 400