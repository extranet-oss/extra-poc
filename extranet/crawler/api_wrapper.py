import json

class IntranetAPIException(RuntimeError):
  def __init__(self, message):
    self.message = message

  def __str__(self):
    return self.message

class IntranetAPI():

  def __init__(self, client):
    self.client = client
    self.token = None

  def set_custom_token(self, token):
    self.token = token

  def locations(self):
    r = self.client.request('location.js', token=self.token)
    if r.status_code != 200:
      raise IntranetAPIException('HTTP/' + str(r.status_code) + ' status code recieved')

    # find bounds of json object inside js code
    start = r.text.find('{')
    if start == -1:
      start = 0
    end = r.text.find('};')
    if end != -1:
      end += 1

    # extract json data
    try:
      data = json.loads(r.text[start:end])
    except:
      raise IntranetAPIException('Invalid JSON recieved')

    return data