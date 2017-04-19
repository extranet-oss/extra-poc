<!DOCTYPE html>
<html>
  <head>
    % if defined('title'):
      <title>{{title}} - extranet</title>
    % else:
      <title>extranet</title>
    % end
    <meta charset="utf-8">
    <link rel="stylesheet" href="/static/css/common.css" type="text/css">
  </head>
  <body>
    % include
    <hr>
    <p>Footer content</p>
    <script src="/static/js/common.js" type="text/javascript"></script>
  </body>
</html>