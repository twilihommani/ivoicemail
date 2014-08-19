import requests
import twilio.twiml
import json

from flask import Flask, request, redirect

app = Flask(__name__)
owner_number = "yourNumber" # To replace
owner_name = "yourName" # To replace
contacts_uri = "contactsAPIUrl" # To replace

@app.route("/", methods=['GET', 'POST'])
def treatCall():
    '''
    This method is the entry point for a caller.
    Generate TwiML according the incomming phone number.
    '''
    # Get the caller's phone number from the incoming Twilio request

    resp = twilio.twiml.Response()
    from_number = request.values.get('From', None)
    if from_number:
        # Need to get rid off spaces and international code because the API store numbers without those two.
        from_number = from_number.replace(" ", "").replace('+33', '0')
    api_response = requests.get(contacts_uri, params={'phone': from_number})
    if api_response.status_code == 200:
        contact = json.loads(api_response.json())
        resp.say("Hello " + contact.get('fname'))
        resp.say(contact.get('speech'))
    else:
        # With an unknown caller, give the oppurtunity to call the owner of the twilio number
        resp.say("Hello. This number belongs to " + owner_name)
        with resp.gather(numDigits=1, action="/owner", method="GET") as g:
            g.say("To call "+ owner_name + " press 1.")
            g.say("To leave a message to "+ owner_name + " press 2.")
            g.say("Press any key to start over")
    return str(resp)

@app.route("/owner", methods=['GET', 'POST'])
def ownerInteraction():
    '''
    We simply call the owner of the application
    '''
    resp = twilio.twiml.Response()
    choices = {"1": callOwner, "2":leaveMsg}

    # Getting client choice
    digit_pressed = request.values.get('Digits', None)
    interaction = choices.get(digit_pressed)

    if interaction:
        return interaction(resp)
    else:
        return redirect('/')


@app.route("/handle-recording", methods=['GET', 'POST'])
def handle_recording():
    """Play back the caller's recording."""
     
    recording_url = request.values.get("RecordingUrl", None)
          
    resp = twilio.twiml.Response()
    resp.say("Thanks for your message.")
    resp.say("We will notify "+ owner_name)
    return str(resp)

def leaveMsg(resp):
    resp.say("Start to talk after the signal. Press any key to stop recording.")
    resp.record(maxLength="30", action="/handle-recording")
    return str(resp)
    

def callOwner(resp):
    resp.dial(owner_number)
    resp.say("Sorry. The call could not be triggered")
    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
