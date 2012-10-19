
import sb.util as util

import errno
import os
import shutil

def make_hash(text):
    import hashlib
    return hashlib.sha1(text).hexdigest()

def pipeline(pipeline_dir, text, fmt):
    text_hash = make_hash(text)
    util.log.info('%s: "%s"', text_hash, text)

    text_dir = os.path.join(pipeline_dir, text_hash)
    original_dir = os.path.join(text_dir, 'original')
    annotations_dir = os.path.join(text_dir, 'annotations')
    export_dir = os.path.join(text_dir, 'export')

    dirs = [original_dir, annotations_dir]
    for d in dirs:
        try:
            os.makedirs(d, mode=0777)
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                pass
            else: raise
        util.system.call_binary('chmod', ['777', d, '-v'])

    shutil.copyfile(os.path.join(pipeline_dir, 'Makefile.example'),
                    os.path.join(text_dir, 'Makefile'))

    text_file = os.path.join(original_dir, 'text.xml')
    if os.path.isfile(text_file):
        util.log.info("File exists and is not rewritten: %s", text_hash)
    else:
        f = open(text_file, 'w')
        f.write('<text>' + text + '</text>')
        f.close()

    make_settings = ['-C', text_dir, 'dir_chmod=777']

    if fmt == 'vrt':
        util.system.call_binary('/bin/make', ['vrt'] + make_settings, verbose=True)

        vrt_file = os.path.join(annotations_dir, 'text.vrt')
        f = open(vrt_file, 'r')
        vrt = f.read()
        f.close()

        return vrt
    else:
        util.system.call_binary('/bin/make', ['export'] + make_settings, verbose=True)

        xml_file = os.path.join(export_dir, 'text.xml')
        f = open(xml_file, 'r')
        xml = f.read()
        f.close()

        return xml


