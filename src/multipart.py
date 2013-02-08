import httplib, mimetypes
import os, stat
from cStringIO import StringIO
import pdb
import mimetools

def request(host, selector, fields, files,method="PUT"):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    boundary, data = multipart_encode(fields, files)
    content_type = 'multipart/form-data; boundary=%s' % boundary
    h = httplib.HTTP(host)
    h.putrequest(method, selector)
    h.putheader('content-type', content_type)
    h.putheader('content-length', str(len(data)))
    h.endheaders()
    h.send(data)
    return h

def multipart_encode(vars, files, boundary = None, buf = None):
    if boundary is None:
        boundary = mimetools.choose_boundary()
    if buf is None:
        buf = StringIO()
    for(key, value) in vars:
        buf.write('--%s\r\n' % boundary)
        buf.write('Content-Disposition: form-data; name="%s"' % key)
        buf.write('\r\n\r\n' + value + '\r\n')
    for(key, fd) in files:
        file_size = os.fstat(fd.fileno())[stat.ST_SIZE]
        filename = fd.name.split('/')[-1]
        contenttype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        buf.write('--%s\r\n' % boundary)
        buf.write('Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (key, filename))
        buf.write('Content-Type: %s\r\n' % contenttype)
        # buffer += 'Content-Length: %s\r\n' % file_size
        fd.seek(0)
        buf.write('\r\n' + fd.read() + '\r\n')
    buf.write('--' + boundary + '--\r\n\r\n')
    buf = buf.getvalue()
    return boundary, buf

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
