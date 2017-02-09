# python-clementine-remote Makefile

.PHONY: compile-protobuf
compile-protobuf:
	protoc -I=protobuf --python_out=clementineremote protobuf/remotecontrolmessages.proto 
   

