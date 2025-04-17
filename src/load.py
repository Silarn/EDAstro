# -*- coding: utf-8 -*-
# EDAstroSync plugin for EDMC
# Source: https://github.com/Silarn/EDAstro
# Licensed under the [GNU Public License (GPL)](http://www.gnu.org/licenses/gpl-2.0.html) version 2 or later.
#
# A simple EDMC plugin to automatically transmit relevant journal data from the
# ED journals to EDAstro.com for record keeping, and scientific purposes.
#
# EDAstro Data charts available at:
# http://edastro.com
###############################################################################

import os
import json
import requests
import tkinter as tk

import semantic_version

from ttkHyperlinkLabel import HyperlinkLabel
from tkinter import messagebox
import myNotebook as nb
import time
from EDMCLogging import get_plugin_logger


# setting up logging
plugin_name = os.path.basename(os.path.dirname(__file__))
logger = get_plugin_logger(f'{plugin_name}')


class This:
    status = tk.StringVar()
    edsm_setting = None
    app_name = 'EDAstro Sync'
    current_version = '1.0.0-rc.1'
    github_latest_release = 'https://api.github.com/repos/Silarn/EDAstro/releases/latest'
    plugin_source = 'https://raw.githubusercontent.com/Silarn/EDAstro/v{}/src/load.py'
    latest_version = None
    latest_version_str = ''
    edastro_get = 'https://edastro.com/api/accepting'
    edastro_push = 'https://edastro.com/api/journal'
    edastro_epoch = 0
    edastro_dict = {}


this = This()
PADX = 10


def plugin_start3(plugin_dir):
    check_version()
    return 'EDAstro Sync'


def plugin_app(parent):
    this.parent = parent
    this.frame = tk.Frame(parent)
    this.frame.columnconfigure(2, weight=1)
    this.status_label = tk.Label(this.frame, anchor=tk.W, textvariable=this.status, wraplength=255)
    this.status_label.grid(row=0, column=1, sticky=tk.W)
    this.status.set('EDAstro Sync: Waiting for data...')
    return this.frame


def plugin_prefs(parent, cmdr, is_beta):
    frame = nb.Frame(parent)
    frame.columnconfigure(5, weight=1)
    try:
        response = requests.get(url = this.github_latest_release)
        data = response.json()
        if response.status_code != requests.codes.ok:
            raise requests.RequestException
        this.latest_version = semantic_version.Version(data['tag_name'][1:])
        this.latest_version_str = str(this.latest_version)
    except (requests.RequestException, requests.JSONDecodeError) as ex:
        logger.error('Failed to parse GitHub release info', exc_info=ex)
    nb.Label(frame, text='EDAstro Sync {INSTALLED}'.format(INSTALLED=this.current_version)) \
        .grid(columnspan=2, padx=PADX, sticky=tk.W)
    if this.latest_version_str:
        nb.Label(frame, text='Latest EDAstro Sync version: {latest_version_str}'.format(latest_version_str=this.latest_version_str)) \
            .grid(columnspan=2, padx=PADX, sticky=tk.W)
    HyperlinkLabel(frame, text='GitHub', background=nb.Label().cget('background'),
                   url='https://github.com/Silarn/EDAstro\n',
                   underline=True).grid(padx=PADX, sticky=tk.W)
    HyperlinkLabel(frame, text='EDAstro', background=nb.Label().cget('background'),
                   url='https://edastro.com\n', underline=True) \
        .grid(padx=PADX, sticky=tk.W)
    return frame


def check_version():
    try:
        response = requests.get(url = this.github_latest_release)
        data = response.json()
        if response.status_code != requests.codes.ok:
            raise requests.RequestException
        this.latest_version = semantic_version.Version(data['tag_name'][1:])
        this.latest_version_str = str(this.latest_version)
        if this.latest_version > semantic_version.Version(this.current_version):
            update_callback()
    except (requests.RequestException, requests.JSONDecodeError) as ex:
        logger.error('Failed to parse GitHub release info', exc_info=ex)


def update_callback():
    this_fullpath = os.path.realpath(__file__)
    this_filepath, this_extension = os.path.splitext(this_fullpath)
    corrected_fullpath = this_filepath + '.py'
    try:
        response = requests.get(this.plugin_source.format(this.latest_version))
        if response.status_code == 200:
            with open(corrected_fullpath, 'wb') as f:
                f.seek(0)
                f.write(response.content)
                f.truncate()
                f.flush()
                os.fsync(f.fileno())
                #this.upgrade_applied = True  # Latch on upgrade successful
                msginfo = ['Version '+this.latest_version_str+' has installed successfully.',
                           'Please close and restart EDMC']
                messagebox.showinfo('EDAstro Sync Update Status', '\n'.join(msginfo))
            logger.info(f'Plugin was updated to {this.latest_version_str}')

        else:
            msginfo = ['An update appears to be available but there was a failure downloading the files.',
                       'You can manually update the plugin or restart EDMC to try again.',
                       'If this continues, please submit an issue on GitHub.']
            messagebox.showinfo('EDAstro Sync Update Status', '\n'.join(msginfo))
            logger.error(f'Failure to update plugin: Bad response\nURL: {this.plugin_source.format(this.latest_version)}')
    except requests.exceptions.RequestException as ex:
        msginfo = ['An update appears to be available but a problem occurred during the download.',
                   'You can manually update the plugin or restart EDMC to try again.',
                   'If this continues, please submit an issue on GitHub.']
        messagebox.showinfo('EDAstro Sync Update Status', '\n'.join(msginfo))
        logger.error(f'Failure to update plugin: Network exception', exc_info=ex)
    except OSError as ex:
        msginfo = ['An update appears to be available but a problem occurred during the download.',
                   'You can manually update the plugin or restart EDMC to try again.',
                   'If this continues, please submit an issue on GitHub.']
        messagebox.showinfo('EDAstro Sync Update Status', '\n'.join(msginfo))
        logger.error(f'Failure to update plugin: OS / write exception', exc_info=ex)


def edastro_update(system, entry, state):
    event_name = str(entry['event'])
    if this.edastro_epoch == 0 or int(time.time()) - this.edastro_epoch > 3600:
        #this.status.set('Retrieving EDAstro events')
        event_list = ''
        try:
            this.edastro_epoch = int(time.time()) - 3000
            response = requests.get(url = this.edastro_get)
            event_json = response.content.strip().decode('utf-8')
            #this.status.set('Event list: '+event_json);
            event_list = json.loads(event_json)
            this.edastro_dict = dict.fromkeys(event_list,1)
            this.edastro_epoch = int(time.time())
            this.status.set('EDAstro Sync: Requested events retrieved')
        except:
            this.status.set('EDAstro Sync: Event retrieval failure!')
    if event_name in this.edastro_dict.keys():
        #this.status.set('Sending EDAstro data...')
        app_header = {'appName': this.app_name, 'appVersion':this.installed_version, 'odyssey':state.get('Odyssey'), 'system':system }
        event_object = [app_header, entry]
        event_data = json.dumps(event_object)
        try:
            json_header = {'Content-Type': 'application/json'}
            response = requests.post(url = this.edastro_push, headers = json_header, data = event_data)
            if response.status_code == 200:
                edastro = json.loads(response.text)
                if str(edastro['status']) == '200' or str(edastro['status']) == '401':
                    # 200 = at least one event accepted, 401 = none were accepted, but no errors either
                    this.status.set(f'EDAstro Sync: Data sent! ({event_name})')
                else:
                    this.status.set('EDAstro Sync: Unexpected Response')
                    logger.debug(f'Error Response:\nRequest: {this.edastro_push}\n Response ({edastro['status']}): \n{edastro['message']}')
            else:
                this.status.set('EDAstro Sync: Unexpected Response')
                logger.debug(f'Unexpected Response:\nRequest: {this.edastro_push}\n Response ({response.status_code}):\n{response.text}')
        except Exception as ex:
            this.status.set('EDAstro Sync: Unexpected Error')
            logger.exception(f'Failed to submit EDAstro data:\nRequest: {this.edastro_push}', exc_info=ex)


def journal_entry(cmdr, is_beta, system, station, entry, state):
    try:
        edastro_update(system, entry, state)
    except Exception as ex:
        this.status.set('EDAstro Sync: Failed to Generate Report')
        logger.exception(f'EDAstro submission failure:\n{entry["event"]}', exc_info=ex)
