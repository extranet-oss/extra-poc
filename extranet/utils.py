def version_tostring(version):
  string = ''
  for num in version:
    string += str(num) + '.'
  return string[:-1]