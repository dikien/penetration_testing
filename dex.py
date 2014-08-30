#!/usr/bin/python
# -*- coding: utf-8 -*-

import zipfile
import os, sys
import glob
import shutil
import struct


root_dir = "/Users/dikien/Downloads/apk/"
os.chdir(root_dir)

files = [x[2] for x in os.walk(root_dir)][0]


#---------------------------------------------------------------------
# isdex : dex 파일이 맞는지 체크
#---------------------------------------------------------------------
def isdex(mm) :
    if mm[0:3] == 'dex' and len(mm) > 0x70 : # 헤더가 'dex' 문자열로 시작하면서 최소 크기가 0x70 Byte 보다 커야 함
        return True
    return False

#-----------------------------------------------------------------
# header : dex 파일의 헤더를 파싱한다.
#-----------------------------------------------------------------
def header(mm) :
    magic           = mm[0:8]
    checksum        = struct.unpack('<L', mm[8:0xC])[0]
    sa1             = mm[0xC:0x20]
    file_size       = struct.unpack('<L', mm[0x20:0x24])[0]
    header_size     = struct.unpack('<L', mm[0x24:0x28])[0]
    endian_tag      = struct.unpack('<L', mm[0x28:0x2C])[0]
    link_size       = struct.unpack('<L', mm[0x2C:0x30])[0]
    link_off        = struct.unpack('<L', mm[0x30:0x34])[0]
    map_off         = struct.unpack('<L', mm[0x34:0x38])[0]
    string_ids_size = struct.unpack('<L', mm[0x38:0x3C])[0]
    string_ids_off  = struct.unpack('<L', mm[0x3C:0x40])[0]
    type_ids_size   = struct.unpack('<L', mm[0x40:0x44])[0]
    type_ids_off    = struct.unpack('<L', mm[0x44:0x48])[0]
    proto_ids_size  = struct.unpack('<L', mm[0x48:0x4C])[0]
    proto_ids_off   = struct.unpack('<L', mm[0x4C:0x50])[0]
    field_ids_size  = struct.unpack('<L', mm[0x50:0x54])[0]
    field_ids_off   = struct.unpack('<L', mm[0x54:0x58])[0]
    method_ids_size = struct.unpack('<L', mm[0x58:0x5C])[0]
    method_ids_off  = struct.unpack('<L', mm[0x5C:0x60])[0]
    class_defs_size = struct.unpack('<L', mm[0x60:0x64])[0]
    class_defs_off  = struct.unpack('<L', mm[0x64:0x68])[0]
    data_size       = struct.unpack('<L', mm[0x68:0x6C])[0]
    data_off        = struct.unpack('<L', mm[0x6C:0x70])[0]

    hdr = {}

    if len(mm) != file_size : # 헤더에 기록된 파일 크기 정보와 실제 파일의 크기가 다르면 분석을 종료한다.
        return False

    hdr['magic'          ] = magic
    hdr['checksum'       ] = checksum
    hdr['sa1'            ] = sa1
    hdr['file_size'      ] = file_size
    hdr['header_size'    ] = header_size
    hdr['endian_tag'     ] = endian_tag
    hdr['link_size'      ] = link_size
    hdr['link_off'       ] = link_off
    hdr['map_off'        ] = map_off
    hdr['string_ids_size'] = string_ids_size
    hdr['string_ids_off' ] = string_ids_off
    hdr['type_ids_size'  ] = type_ids_size
    hdr['type_ids_off'   ] = type_ids_off
    hdr['proto_ids_size' ] = proto_ids_size
    hdr['proto_ids_off'  ] = proto_ids_off
    hdr['field_ids_size' ] = field_ids_size
    hdr['field_ids_off'  ] = field_ids_off
    hdr['method_ids_size'] = method_ids_size
    hdr['method_ids_off' ] = method_ids_off
    hdr['class_defs_size'] = class_defs_size
    hdr['class_defs_off' ] = class_defs_off
    hdr['data_size'      ] = data_size
    hdr['data_off'       ] = data_off

    return hdr


#---------------------------------------------------------------------
# string_id_list : dex 파일의 문자열 리스트를 추출한다.
#---------------------------------------------------------------------
def string_id_list(mm, hdr) :
    string_id = [] # 전체 문자열을 담을 리스트

    string_ids_size = hdr['string_ids_size']
    string_ids_off  = hdr['string_ids_off' ]

    for i in range(string_ids_size) :
        off = struct.unpack('<L', mm[string_ids_off+(i*4):string_ids_off+(i*4)+4])[0]
        c_size = ord(mm[off])
        c_char = mm[off+1:off+1+c_size]

        string_id.append(c_char)

    return string_id

#---------------------------------------------------------------------
# type_id_list : dex 파일의 type 리스트를 추출한다.
#---------------------------------------------------------------------
def type_id_list(mm, hdr) :
    type_list = [] # 전체 Type 정보를 담을 리스트

    type_ids_size = hdr['type_ids_size'  ]
    type_ids_off  = hdr['type_ids_off'   ]

    for i in range(type_ids_size) :
        idx = struct.unpack('<L', mm[type_ids_off+(i*4):type_ids_off+(i*4)+4])[0]

        type_list.append(idx)

    return type_list


#---------------------------------------------------------------------
# proto_id_list : dex 파일의 prototype 리스트를 추출한다.
#---------------------------------------------------------------------
def proto_id_list(mm, hdr) :
    proto_list = []

    proto_ids_size = hdr['proto_ids_size'  ]
    proto_ids_off  = hdr['proto_ids_off'   ]

    for i in range(proto_ids_size) :
        shorty_idx      = struct.unpack('<L', mm[proto_ids_off+(i*12)  :proto_ids_off+(i*12)+ 4])[0]
        return_type_idx = struct.unpack('<L', mm[proto_ids_off+(i*12)+4:proto_ids_off+(i*12)+ 8])[0]
        param_off       = struct.unpack('<L', mm[proto_ids_off+(i*12)+8:proto_ids_off+(i*12)+12])[0]

        proto_list.append([shorty_idx, return_type_idx, param_off])

    return proto_list


#-----------------------------------------------------------------
# field_id_list : dex 파일의 field 리스트를 추출한다.
#-----------------------------------------------------------------
def field_id_list(mm, hdr) :
    field_list = []

    field_ids_size = hdr['field_ids_size'  ]
    field_ids_off  = hdr['field_ids_off'   ]

    for i in range(field_ids_size) :
        class_idx = struct.unpack('<H', mm[field_ids_off+(i*8)  :field_ids_off+(i*8)+2])[0]
        type_idx  = struct.unpack('<H', mm[field_ids_off+(i*8)+2:field_ids_off+(i*8)+4])[0]
        name_idx  = struct.unpack('<L', mm[field_ids_off+(i*8)+4:field_ids_off+(i*8)+8])[0]

        field_list.append([class_idx, type_idx, name_idx])

    return field_list



#-----------------------------------------------------------------
# method_id_list : dex 파일의 method 리스트를 추출한다.
#-----------------------------------------------------------------
def method_id_list(mm, hdr) :
    method_list = []

    method_ids_size = hdr['method_ids_size']
    method_ids_off  = hdr['method_ids_off']

    for i in range(method_ids_size) :
        class_idx = struct.unpack('<H', mm[method_ids_off+(i*8)  :method_ids_off+(i*8)+2])[0]
        proto_idx = struct.unpack('<H', mm[method_ids_off+(i*8)+2:method_ids_off+(i*8)+4])[0]
        name_idx  = struct.unpack('<L', mm[method_ids_off+(i*8)+4:method_ids_off+(i*8)+8])[0]

        method_list.append([class_idx, proto_idx, name_idx])

    return method_list





for file in files:

    # filename에 파일의 이름을 저장
    filename = os.path.splitext(file)[0]
    # extension에 파일의 확장자를 저장
    extension = os.path.splitext(file)[1]

    # apk파일은 zip파일 형식이므로 zip파일인지 여부를 테스트
    if zipfile.is_zipfile(file) is True:

        print "[+] step - 1 ZIP파일 확인"

        # zip파일을 f변수로 받음
        f = open(file, 'rb')

        try:
            # apk파일의 압축을 풀어서 새로운 디렉토리에 저장
            with zipfile.ZipFile(file, "r") as z:
                output_dir = root_dir + filename
                z.extractall(output_dir)
                print "[+] step - 2 압축풀기 성공"
        except:
            print "[+] 압축풀기 실패"
            sys.exit()

        f.close()

        dexfilelist = glob.glob(output_dir + "/*.dex")

        if len(dexfilelist) == 1:

            dexfile = dexfilelist[0]

            f = open(dexfile, 'rb')
            mm = f.read()

            if isdex(mm):
                print "[+] Step - 3 dex 파일포맷 확인"
            else:
                print "[+] Step - 3 Fail"

            hdr = header(mm)
            if hdr != False:
                print "[+] Step - 4 dex 헤더정보 확인"
                for i in hdr.keys():
                    print "%s : %s" %(i, hdr[i])
            else:
                print "[+] Step - 4 Fail"


            try:
                string_ids = string_id_list(mm, hdr)
                print "[+] Step - 5 String 추출 성공"
                for i in range(len(string_ids)) :
                    print '[%4d] %s' % (i, string_ids[i])
            except:
                print "[+] Step - 5 Fail"


            try:
                type_ids = type_id_list(mm, hdr)
                print "[+] Step - 6 Type IDs 리스트 추출 성공"
                for i in range(len(type_ids)):
                     string_idx = type_ids[i]
                     print '[%4d] %s' % (i, string_ids[string_idx])
            except:
                print "[+] Step - 6 Fail"


            try:
                proto_ids = proto_id_list(mm, hdr)
                print "[+] Step - 7 proto id list 추출 성공"
                for i in range(len(proto_ids)):
                    proto = proto_ids[i]
                    idx   = proto[0] # shorty_idx
                    print '[%4d] %s' % (i, string_ids[idx])
            except:
                print "[+] Step - 7 Fail"


            try:
                field_ids = field_id_list(mm, hdr)
                print "[+] Step - 8 field id list 추출 성공"
                for i in range(len(field_ids)) :
                    (class_idx, type_idx, name_idx) = field_ids[i]

                    class_str = string_ids[type_ids[class_idx]]
                    type_str  = string_ids[type_ids[type_idx]]
                    name_str  = string_ids[name_idx]

                    mag = '%s %s.%s' % (type_str, class_str, name_str)
                    print '[%4d] %s' % (i, mag)
            except:
                print "[+] Step - 8 Fail"


            try:
                method_ids = method_id_list(mm, hdr)
                print "[+] Step - 9 method list 추출 성공"
                for i in range(len(method_ids)) :
                    (class_idx, proto_idx, name_idx) = method_ids[i]
                    class_str = string_ids[type_ids[class_idx]]
                    name_str  = string_ids[name_idx]

                    print '[%04d] %s.%s()' % (i, class_str, name_str)

            except:
                print "[+] Step - 9 Fail"


            # print hdr['class_defs_size']      # 전체 Class 정보 개수
            # print hex(hdr['class_defs_off'])  # 전체 Class 정보의 시작 위치


            f.close()

        shutil.rmtree(root_dir + filename)
        print "%s 폴더가 정상적으로 삭제되었습니다." % root_dir + filename





