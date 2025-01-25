INSTALL_DIR := /srv/puvefa
PYTHON := python3



install:
	$(info Installing on ${INSTALL_DIR})
	mkdir -p $(INSTALL_DIR)
	cp -r ../src/ $(INSTALL_DIR)
	cp ../requirements.txt $(INSTALL_DIR)
	cd $(INSTALL_DIR)
	$(PYTHON) -m venv $(INSTALL_DIR)/env
	/bin/bash $(INSTALL_DIR)/env/bin/activate
	$(INSTALL_DIR)/env/bin/python3 -m pip install -r $(INSTALL_DIR)/requirements.txt
	$(INSTALL_DIR)/env/bin/python3 -m pip install gunicorn
	$(INSTALL_DIR)/env/bin/python3 $(INSTALL_DIR)/src/manage.py migrate
	$(INSTALL_DIR)/env/bin/python3 $(INSTALL_DIR)/src/manage.py collectstatic
	cp puvefa_nginx.conf /etc/nginx/sites-available/
	ln -s /etc/nginx/sites-available/puvefa_nginx.conf /etc/nginx/sites-enabled
	systemctl restart nginx.service
	cp puvefa_gunicorn.service /etc/systemd/system/
	cp puvefa_gunicorn.socket /etc/systemd/system/
	systemctl start puvefa_gunicorn.socket
	systemctl enable puvefa_gunicorn.socket
	systemctl start puvefa_gunicorn.service
	systemctl enable puvefa_gunicorn.service

uninstall:
	$(info Uninstalling from $(INSALL_DIR))
	systemctl stop puvefa_gunicorn.service
	systemctl disable puvefa_gunicorn.service
	systemctl stop puvefa_gunicorn.socket
	systemctl disable puvefa_gunicorn.socket

	rm -i /etc/systemd/system/puvefa_gunicorn.socket	
	rm -i /etc/systemd/system/puvefa_gunicorn.service	
	rm -i /etc/nginx/sites-available/puvefa_nginx.conf
	rm -i /etc/nginx/sites-enabled/puvefa_nginx.conf
