from BaseService import BaseService
import subprocess

class Service(BaseService):
    def start(self):
        retVal = True
        # create the voip directories, if needed
        if not os.path.exists('/usr/local/etc/afelio'):
            os.mkdir('/usr/local/etc/afelio')
        if not os.path.exists('/var/run/afelio'):
            os.mkdir('/var/run/afelio')
        if not os.path.exists('/var/spool/afelio/outgoing'):
            os.makedirs('/var/spool/afelio/outgoing')

        # create voip config files from CF config
        # adsi.conf
        f = open('/usr/local/etc/afelio/adsi.conf', 'w')
        f.write('[intro]\n')
        f.write('alignment = %s\n' % (self.config.getVar('svc.voip.adsi.intro.alignment')))
        for val in self.config.getVar('svc.voip.adsi.intro.greeting'):
            f.write('greeting => '+val+'\n')
        f.close()

        # adtranvofr.conf
        f = open('/usr/local/etc/afelio/adtranvofr.conf', 'w')
        f.write('[interfaces]\n')
        f.write('language %s\n' % (self.config.getVar('svc.voip.language')))
        f.write('context=default\n')
        for val in self.config.getVar('svc.voip.adtranvofr.user'):
            f.write('user => '+val+'\n')
        f.write('context=remote\n')
        for val in self.config.getVar('svc.voip.adtranvofr.network'):
            f.write('network => '+val+'\n')
        f.close()

        # agents.conf
        f = open('/usr/local/etc/afelio/agents.conf', 'w')
        f.write('[general]\n')
        f.write('persistentagents=yes\n')
        f.write('[agents]\n')
        f.close()

        # alarmreceiver.conf
        f = open('/usr/local/etc/afelio/alarmreceiver.conf', 'w')
        f.write('[general]\n')
        f.write('timestampformat = %a %b %d, %Y @ %H:%M:%S %Z\neventspooldir = /tmp\nlogindividualevents = no\nfdtimeout = 2000\nsdtimeout = 200\nloudness = 8192\n')
        f.close()

        # alsa.conf
        f = open('/usr/local/etc/afelio/alsa.conf', 'w')
        f.write('[general]\n')
        f.write('autoanswer=yes\ncontext=local\nextension=s\n')
        f.close()

        # amd.conf
        f = open('/usr/local/etc/afelio/amd.conf', 'w')
        f.write('[general]\n')
        f.write('initial_silence = 2500\ngreeting = 1500\nafter_greeting_silence = 800\ntotal_analysis_time = 5000\nmin_word_length = 100\nbetween_words_silence = 50\nmaximum_number_of_words = 3\nsilence_threshold = 256\n')
        f.close()

        # asterisk.adsi
        f = open('/usr/local/etc/afelio/asterisk.adsi', 'w')
        f.write('DESCRIPTION "Asterisk PBX"\nVERSION 0x00\nSECURITY 0X9BDBF7AC\nFDN 0x0000000F\nFLAG "nocallwaiting"\nDISPLAY "titles" IS "** Asterisk PBX **"\nDISPLAY "talkingto" IS "Call active." JUSTIFY LEFT\nDISPLAY "callname" IS "$Call1p" JUSTIFY LEFT\nDISPLAY "callnum" IS "$Call1s" JUSTIFY LEFT\nDISPLAY "incoming" IS "Incoming call!" JUSTIFY LEFT\nDISPLAY "ringing" IS "Calling... " JUSTIFY LEFT\nDISPLAY "callended" IS "Call ended." JUSTIFY LEFT\nDISPLAY "missedcall" IS "Missed call." JUSTIFY LEFT\nDISPLAY "busy" IS "Busy." JUSTIFY LEFT\nDISPLAY "reorder" IS "Reorder." JUSTIFY LEFT\nDISPLAY "cwdisabled" IS "Callwait disabled"\nDISPLAY "empty" IS "asdf"\n')
        f.write('KEY "callfwd" IS "CallFwd" OR "Call Forward"\n\tOFFHOOK\n\tVOICEMODE\n\tWAITDIALTONE\n\tSENDDTMF "*60"\n\tGOTO "offHook"\nENDKEY\n')
        f.write('KEY "vmail_OH" IS "VMail" OR "Voicemail"\n\tOFFHOOK\n\tVOICEMODE\n\tWAITDIALTONE\n\tSENDDTMF "8500"\nENDKEY\n')
        f.write('KEY "vmail" IS "VMail" OR "Voicemail"\n\tSENDDTMF "8500"\nENDKEY')
        f.write('KEY "backspace" IS "BackSpc" OR "Backspace"\n\tBACKSPACE\nENDKEY')
        f.write('KEY "cwdisable" IS "CWDsble" OR "Disable Call Wait"\n\tSENDDTMF "*70"\n\tSETFLAG "nocallwaiting"\n\tSHOWDISPLAY "cwdisabled" AT 4\n\tTIMERCLEAR\n\tTIMERSTART 1\nENDKEY')
        f.write('KEY "cidblock" IS "CIDBlk" OR "Block Callerid"\n\tSENDDTMF "*67"\n\tSETFLAG "nocallwaiting"\nENDKEY')
        f.write('SUB "main" IS\n\tIFEVENT NEARANSWER THEN\n\t\tCLEAR\n\t\tSHOWDISPLAY "titles" AT 1 NOUPDATE\n\t\tSHOWDISPLAY "talkingto" AT 2 NOUPDATE\n\t\tSHOWDISPLAY "callname" AT 3\n\t\tSHOWDISPLAY "callnum" AT 4\n\t\tGOTO "stableCall"\n\tENDIF\n\tIFEVENT OFFHOOK THEN\n\t\tCLEAR\n\t\tCLEARFLAG "nocallwaiting"\n\t\tCLEARDISPLAY\n\t\tSHOWDISPLAY "titles" AT 1\n\t\tSHOWKEYS "vmail"\n\t\tSHOWKEYS "cidblock"\n\t\tSHOWKEYS "cwdisable" UNLESS "nocallwaiting"\n\t\tGOTO "offHook"\n\tENDIF\n\tIFEVENT IDLE THEN\n\t\tCLEAR\n\t\tSHOWDISPLAY "titles" AT 1\n\t\tSHOWKEYS "vmail_OH"\n\tENDIF\n\tIFEVENT CALLERID THEN\n\t\tCLEAR\n\t\tSHOWDISPLAY "callname" AT 3 NOUPDATE\n\t\tSHOWDISPLAY "callnum" AT 4\n\tENDIF\n\tIFEVENT RING THEN\n\t\tCLEAR\n\t\tSHOWDISPLAY "titles" AT 1 NOUPDATE\n\t\tSHOWDISPLAY "incoming" AT 2\n\tENDIF\n\tIFEVENT ENDOFRING THEN\n\t\tSHOWDISPLAY "missedcall" AT 2\n\t\tCLEAR\n\t\tSHOWDISPLAY "titles" AT 1\n\t\tSHOWKEYS "vmail_OH"\n\tENDIF\n\tIFEVENT TIMER THEN\n\t\tCLEAR\n\t\tSHOWDISPLAY "empty" AT 4\n\tENDIF\nENDSUB')
        f.write('SUB "offHook" IS\n\tIFEVENT FARRING THEN\n\t\tCLEAR\n\t\tSHOWDISPLAY "titles" AT 1 NOUPDATE\n\t\tSHOWDISPLAY "ringing" AT 2 NOUPDATE\n\t\tSHOWDISPLAY "callname" at 3 NOUPDATE\n\t\tSHOWDISPLAY "callnum" at 4\n\tENDIF\n\tIFEVENT FARANSWER THEN\n\t\tCLEAR\n\t\tSHOWDISPLAY "talkingto" AT 2\n\t\tGOTO "stableCall"\n\tENDIF\n\tIFEVENT BUSY THEN\n\t\tCLEAR\n\t\tSHOWDISPLAY "titles" AT 1 NOUPDATE\n\t\tSHOWDISPLAY "busy" AT 2 NOUPDATE\n\t\tSHOWDISPLAY "callname" at 3 NOUPDATE\n\t\tSHOWDISPLAY "callnum" at 4\n\tENDIF\n\tIFEVENT REORDER THEN\n\t\tCLEAR\n\t\tSHOWDISPLAY "titles" AT 1 NOUPDATE\n\t\tSHOWDISPLAY "reorder" AT 2 NOUPDATE\n\t\tSHOWDISPLAY "callname" at 3 NOUPDATE\n\t\tSHOWDISPLAY "callnum" at 4\n\tENDIF\nENDSUB')
        f.write('SUB "stableCall" IS\n\tIFEVENT REORDER THEN\n\t\tSHOWDISPLAY "callended" AT 2\n\tENDIF\nENDSUB')
        f.close()

        # asterisk.conf
        f = open('/usr/local/etc/afelio/asterisk.conf', 'w')
        f.write('[directories]')
        f.write('astetcdir => /usr/local/etc/afelio\nastmoddir => /usr/local/lib/afelio/modules\nastvarlibdir => /usr/local/share/afelio\nastdatadir => /usr/local/share/afelio\nastagidir => /usr/local/share/afelio/agi-bin\nastspooldir => /var/spool/afelio\nastrundir => /var/run/afelio\nastlogdir => /var/log/afelio')
        f.write('[options]')
        f.write('internal_timing = yes')
        f.write('[codec_negotiation]')
        f.write('translation_algorithm = strict')
        f.close()

        # cdr.conf
        f = open('/usr/local/etc/afelio/cdr.conf', 'w')
        f.write('[general]')
        f.write('enable=no')
        f.write('[csv]\nusegmtime=yes\nloguniqueid=yes\nloguserfield=yes')
        f.close()

        # codecs.conf
        f = open('/usr/local/etc/afelio/codecs.conf', 'w')
        f.write('[speex]\nquality => 3\ncomplexity => 2\nenhancement => true\nvad => true\nvbr => true\nabr => 0\nvbr_quality => 4\ndtx => false\npreprocess => false\npp_vad => false\npp_agc => false\npp_agc_level => 8000\npp_denoise => false\npp_dereverb => false\npp_dereverb_decay => 0.4\npp_dereverb_level => 0.3')
        f.write('[plc]\ngenericplc => true')
        f.close()

        # dnsmgr.conf
        f = open('/usr/local/etc/afelio/dnsmgr.conf', 'w')
        f.write('[general]\nenable=no\nrefreshinterval=1200')
        f.close()

        # dundi.conf
        f = open('/usr/local/etc/afelio/dundi.conf', 'w')
        f.write('[general]')
        f.write('ttl=32\nautokill=yes\n')
        f.write('[mappings]')
        f.close()

        # enum.conf
        f = open('/usr/local/etc/afelio/enum.conf', 'w')
        f.write('[general]\nsearch => e164.arpa\nh323driver => H323')
        f.close()

        # extconfig.conf
        f = open('/usr/local/etc/afelio/extconfig.conf', 'w')
        f.write('[settings]')
        f.close()

        # extensions.ael
        f = open('/usr/local/etc/afelio/extensions.ael', 'w')
        f.write('globals {\n\tCONSOLE="Console/dsp";\n\tIAXINFO=guest;\n\tTRUNK="Zap/g2";\n\tTRUNKMSD=1;\n};')
        f.write('context ael-iaxtel700 {\n\t_91700XXXXXXX => Dial(IAX2/${IAXINFO}@iaxtel.com/${EXTEN:1}@iaxtel);\n};')
        f.close()

        # extensions.conf
        f = open('/usr/local/etc/afelio/extensions.conf', 'w')
        # write sections to file in order
        for section in self.config.getVar('svc.voip.extensions._index'):
            f.write('[%s]\n' % (section))
            for key, val in self.config.getVars('svc.voip.extensions.%s.*' % (section)).iteritems():
                var = key.split('.')[4]
                if var == 'exten':
                    exten_name = key.split('.')[5]
                    exten_type = val
                    if exten_type == 'echo':
                        f.write('exten => %s,1,Answer()\n' % (exten_name))
                        f.write('exten => %s,n,Wait(1)\n' % (exten_name))
                        f.write('exten => %s,n,Playback(tt-weasels)\n' % (exten_name))
                        f.write('exten => %s,n,Playback(tt-monkeysintro)\n' % (exten_name))
                        f.write('exten => %s,n,Playback(tt-monkeys)\n' % (exten_name))
                        f.write('exten => %s,n,Verbose(1|Echo test application)\n' % (exten_name))
                        f.write('exten => %s,n,Echo()\n' % (exten_name))
                        f.write('exten => %s,n,Hangup()\n' % (exten_name))
                    elif exten_type == 'echo_basic':
                        f.write('exten => %s,1,Answer()\n' % (exten_name))
                        f.write('exten => %s,n,Echo()\n' % (exten_name))
                        f.write('exten => %s,n,Hangup()\n' % (exten_name))
                    elif exten_type == 'sip':
                        f.write('exten => %s,1,Verbose(1|Extension %s)\n' % (exten_name, exten_name))
                        f.write('exten => %s,n,Dial(SIP/%s|30)\n' % (exten_name, exten_name))
                        f.write('exten => %s,n,Hangup()\n' % (exten_name))
                    elif exten_type == 'unrouted':
                        f.write('exten => %s,1,Verbose(1|Unrouted call handler)\n' % (exten_name))
                        f.write('exten => %s,n,Answer()\n' % (exten_name))
                        f.write('exten => %s,n,Wait(1)\n' % (exten_name))
                        f.write('exten => %s,n,Playback(tt-weasels)\n' % (exten_name))
                        f.write('exten => %s,n,Hangup()\n' % (exten_name))
                    elif exten_type == 'h323':
                        pass
                    elif exten_type == 'iax':
                        pass
                elif var == 'include':
                    f.write('%s => %s\n' % (var, val))
                else:
                    f.write('%s = %s\n' % (var, val))
        f.close()

        # features.conf
        f = open('/usr/local/etc/afelio/features.conf', 'w')
        f.write('[general]\nparkext => 700\nparkpos => 701-720\ncontext => parkedcalls')
        f.write('[featuremap]')
        f.write('[applicationmap]')
        f.close()

        # festival.conf
        f = open('/usr/local/etc/afelio/festival.conf', 'w')
        f.write('[general]')
        f.close()

        # followme.conf
        f = open('/usr/local/etc/afelio/followme.conf', 'w')
        f.write('[general]\nfeaturedigittimeout=>5000\ntakecall=>1\ndeclinecall=>2\ncall-from-prompt=>followme/call-from\nnorecording-prompt=>followme/no-recording\noptions-prompt=>followme/options\npls-hold-prompt=>followme/pls-hold-while-try\nstatus-prompt=>followme/status\nsorry-prompt=>followme/sorry')
        f.write('[default]\nmusicclass=>default\ncontext=>default\nnumber=>01233456,25\ntakecall=>1\ndeclinecall=>2\ncall-from-prompt=>followme/call-from\nfollowme-norecording-prompt=>followme/no-recording\nfollowme-options-prompt=>followme/followme-options\nfollowme-pls-hold-prompt=>followme/pls-hold-while-try\nfollowme-status-prompt=>followme/followme-status\nfollowme-sorry-prompt=>followme/followme-sorry\n')
        f.close()

        # func_odbc.conf
        f = open('/usr/local/etc/afelio/func_odbc.conf', 'w')
        f.write('[SQL]\ndsn=mysql1\nread=%{ARG}')
        f.write('[ANTIGF]\ndsn=mysql1\nread=SELECT COUNT(*) FROM exgirlfriends WHERE callerid=\'${SQL_ESC(${ARG1})}\'')
        f.write('[PRESENCE]\ndsn=mysql1\nread=SELECT location FROM presence WHERE id=\'${SQL_ESC(${ARG1})}\'\nwrite=UPDATE presence SET location=\'${SQL_ESC(${VAL1})}\' WHERE id=\'${SQL_ESC(${ARG1})}\'')
        f.close()

        # gtalk.conf
        f = open('/usr/local/etc/afelio/gtalk.conf', 'w')
        f.write('')
        f.close()

        # h323.conf
        f = open('/usr/local/etc/afelio/h323.conf', 'w')
        f.write('[general]\nport = 1720')
        f.close()

        # http.conf
        f = open('/usr/local/etc/afelio/http.conf', 'w')
        f.write('[general]\nenabled=no\nenablestatic=no\nbindaddr=127.0.0.1\nbindport=8088\n')
        f.close()

        # iax.conf
        f = open('/usr/local/etc/afelio/iax.conf', 'w')
        f.write('[general]\nadsi=no\nbandwidth=low\ndisallow=lpc10\njitterbuffer=no\nforcejitterbuffer=no\nautokill=yes')
        f.write('[guest]\ntype=user\ncontext=default\ncallerid="Guest IAX User"')
        f.write('[iaxtel]\ntype=user\ncontext=default\nauth=rsa\ninkeys=iaxtel')
        f.write('[iaxfwd]\ntype=user\ncontext=default\nauth=rsa\ninkeys=freeworlddialup')
        f.write('[demo]\ntype=peer\nusername=afelio\nsecret=supersecret\nhost=216.207.245.47\n')
        f.close()

        # iaxprov.conf
        f = open('/usr/local/etc/afelio/iaxprov.conf', 'w')
        f.write('[default]\nlanguage=en\ncodec=ulaw\nflags=register,heartbeat')
        f.close()

        # indications.conf
        f = open('/usr/local/etc/afelio/indications.conf', 'w')
        f.write('[general]\ncountry=us')
        f.write('[at]\ndescription = Austria\nringcadence = 1000,5000\ndial = 420\nbusy = 420/400,0/400\nring = 420/1000,0/5000\ncongestion = 420/200,0/200\ncallwaiting = 420/40,0/1960\ndialrecall = 420\nrecord = 1400/80,0/14920\ninfo = 950/330,1450/330,1850/330,0/1000\nstutter = 380+420')
        f.write('[au]\ndescription = Australia\nringcadence = 400,200,400,2000\ndial = 413+438\nbusy = 425/375,0/375\nring = 413+438/400,0/200,413+438/400,0/2000\ncongestion = 425/375,0/375,420/375,0/375\ncallwaiting = 425/200,0/200,425/200,0/4400\ndialrecall = 413+438\nrecord = !425/1000,!0/15000,425/360,0/15000\ninfo = 425/2500,0/500\nstd = !525/100,!0/100,!525/100,!0/100,!525/100,!0/100,!525/100,!0/100,!525/100\nfacility = 425\nstutter = 413+438/100,0/40\nringmobile = 400+450/400,0/200,400+450/400,0/2000')
        # include the rest of the list in here at some point
        f.write('[us]\ndescription = United States / North America\nringcadence = 2000,4000\ndial = 350+440\nbusy = 480+620/500,0/500\nring = 440+480/2000,0/4000\ncongestion = 480+620/250,0/250\ncallwaiting = 440/300,0/10000\ndialrecall = !350+440/100,!0/100,!350+440/100,!0/100,!350+440/100,!0/100,350+440\nrecord = 1400/500,0/15000\ninfo = !950/330,!1400/330,!1800/330,0\nstutter = !350+440/100,!0/100,!350+440/100,!0/100,!350+440/100,!0/100,!350+440/100,!0/100,!350+440/100,!0/100,!350+440/100,!0/100,350+440')
        f.write('[us-old]\ndescription = United States Circa 1950/ North America\nringcadence = 2000,4000\ndial = 600*120\nbusy = 500*100/500,0/500\nring = 420*40/2000,0/4000\ncongestion = 500*100/250,0/250\ncallwaiting = 440/300,0/10000\ndialrecall = !600*120/100,!0/100,!600*120/100,!0/100,!600*120/100,!0/100,600*120\nrecord = 1400/500,0/15000\ninfo = !950/330,!1400/330,!1800/330,0\nstutter = !600*120/100,!0/100,!600*120/100,!0/100,!600*120/100,!0/100,!600*120/100,!0/100,!600*120/100,!0/100,!600*120/100,!0/100,600*120')
        f.close()

        # jabber.conf
        f = open('/usr/local/etc/afelio/jabber.conf', 'w')
        f.write('[general]')
        f.close()

        # logger.conf
        f = open('/usr/local/etc/afelio/logger.conf', 'w')
        # write sections to file in order
        for i in self.config.getVar('svc.voip.logger._index'):
            f.write('['+i+']\n')
            for key, val in self.config.getVars('svc.voip.logger.'+i+'.*').iteritems():
                f.write(key.split('.')[4]+' = '+val+'\n')
        f.close()

        # manager.conf
        f = open('/usr/local/etc/afelio/manager.conf', 'w')
        f.write('[general]\ndisplaysystemname = yes\nenabled = no\nwebenabled = no\nport = 5038\nbindaddr = 0.0.0.0')
        f.close()

        # meetme.conf
        f = open('/usr/local/etc/afelio/meetme.conf', 'w')
        f.write('[general]')
        f.write('[rooms]')
        f.close()

        # mgcp.conf
        f = open('/usr/local/etc/afelio/mgcp.conf', 'w')
        f.write('[general]')
        f.close()

        # misdn.conf
        f = open('/usr/local/etc/afelio/misdn.conf', 'w')
        f.write('[general]\nmisdn_init=/etc/misdn-init.conf\ndebug=0\nntdebugflags=0\nntdebugfile=/var/log/misdn-nt.log\nbridging=no\nl1watcher_timeout=0\nstop_tone_after_first_digit=yes\nappend_digits2exten=yes\ndynamic_crypt=no\ncrypt_prefix=**\ncrypt_keys=test,muh')
        f.write('[default]\ncontext=misdn\nlanguage=en\nmusicclass=default\nsenddtmf=yes\nfar_alerting=no\nallowed_bearers=all\nnationalprefix=0\ninternationalprefix=00\nrxgain=0\ntxgain=0\nte_choose_channel=no\npmp_l1_check=no\npp_l2_check=no\nreject_cause=16\nneed_more_infos=no\nnttimeout=no\nmethod=standard\ndialplan=0\nlocaldialplan=0\ncpndialplan=0\nearly_bconnect=yes\nincoming_early_audio=no\nnodialtone=no\npresentation=-1\nscreen=-1\nechocancelwhenbridged=no\nechotraining=no\njitterbuffer=4000\njitterbuffer_upper_threshold=0\nhdlc=no\nmax_incoming=-1\nmax_outgoing=-1')
        f.write('[intern]\nports=1,2\ncontext=Intern')
        f.write('[internPP]\nports=3')
        f.write('[first_extern]\nports=4\ncontext=Extern1\nmsns=*')
        f.close()

        # modem.conf
        f = open('/usr/local/etc/afelio/modem.conf', 'w')
        f.write('[interfaces]\ncontext=remote\ndriver=aopen\nlanguage=en\nstripmsd=0\ndialtype=tone\nmode=immediate\ngroup=1')
        f.close()

        # modules.conf
        f = open('/usr/local/etc/afelio/modules.conf', 'w')
        f.write('[modules]\nautoload=yes\nnoload => pbx_gtkconsole.so\nnoload => pbx_kdeconsole.so\nload => res_musiconhold.so\nnoload => chan_alsa.so')
        f.close()

        # musiconhold.conf
        f = open('/usr/local/etc/afelio/musiconhold.conf', 'w')
        f.write('[default]\nmode=files\ndirectory=/usr/local/share/afelio/moh\nrandom=yes')
        f.close()

        # muted.conf
        f = open('/usr/local/etc/afelio/muted.conf', 'w')
        f.write('host localhost\nuser user\npass pass\nchannel Zap/1\nchannel Zap/2\nchannel SIP/mark\nmutelevel 20\nsmoothfade')
        f.close()

        # osp.conf
        f = open('/usr/local/etc/afelio/osp.conf', 'w')
        f.write('[general]')
        f.close()

        # oss.conf
        f = open('/usr/local/etc/afelio/oss.conf', 'w')
        f.write('[general]')
        f.write('[card1]')
        f.close()

        # phone.conf
        f = open('/usr/local/etc/afelio/phone.conf', 'w')
        f.write('[interfaces]\nmode=immediate\nformat=slinear\nechocancel=medium')
        f.close()

        # privacy.conf
        f = open('/usr/local/etc/afelio/privacy.conf', 'w')
        f.write('[general]\nmaxretries = 2')
        f.close()

        # queues.conf
        f = open('/usr/local/etc/afelio/queues.conf', 'w')
        f.write('[general]\npersistentmembers = yes\nautofill = yes\nmonitor-type = MixMonitor')
        f.close()

        # res_snmp.conf
        f = open('/usr/local/etc/afelio/res_snmp.conf', 'w')
        f.write('[general]\nenabled=no')
        f.close()

        # rpt.conf
        f = open('/usr/local/etc/afelio/rpt.conf', 'w')
        f.close()

        # rtp.conf
        f = open('/usr/local/etc/afelio/rtp.conf', 'w')
        f.write('[general]\nrtpstart=10000\nrtpend=20000\nrtpchecksums=no')
        f.close()

        # say.conf
        f = open('/usr/local/etc/afelio/say.conf', 'w')
        f.write('[digit-base](!)\n_digit:[0-9] => digits/${SAY}\n_digit:[-] => letters/dash\n_digit:[*] => letters/star\n_digit:[@] => letters/at\n_digit:[0-9]. => digit:${SAY:0:1}, digit:${SAY:1}')
        f.write('[date-base](!)\n_date:Y:. => num:${SAY:0:4} ; year, 19xx\n_date:[Bb]:. => digits/mon-$[${SAY:4:2}-1]\n_date:[Aa]:. => digits/day-${SAY:16:1}\n_date:[de]:. => num:${SAY:6:2}\n_date:[hH]:. => num:${SAY:8:2}\n_date:[I]:. => num:$[${SAY:8:2} % 12]\n_date:[M]:. => num:${SAY:10:2}\n_date:[pP]:. => digits/p-m\n_date:[S]:. => num:${SAY:13:2}')
        f.write('[en-base](!)\n_[n]um:0. => num:${SAY:1}\n_[n]um:X => digits/${SAY}\n_[n]um:1X => digits/${SAY}\n_[n]um:[2-9]0 =>  digits/${SAY}\n_[n]um:[2-9][1-9] =>  digits/${SAY:0:1}0, num:${SAY:1}\n_[n]um:XXX => num:${SAY:0:1}, digits/hundred, num:${SAY:1}\n_[n]um:XXXX => num:${SAY:0:1}, digits/thousand, num:${SAY:1}\n_[n]um:XXXXX => num:${SAY:0:2}, digits/thousand, num:${SAY:2}\n_[n]um:XXXXXX => num:${SAY:0:3}, digits/thousand, num:${SAY:3}\n_[n]um:XXXXXXX => num:${SAY:0:1}, digits/million, num:${SAY:1}\n_[n]um:XXXXXXXX => num:${SAY:0:2}, digits/million, num:${SAY:2}\n_[n]um:XXXXXXXXX => num:${SAY:0:3}, digits/million, num:${SAY:3}\n_[n]um:XXXXXXXXXX => num:${SAY:0:1}, digits/billion, num:${SAY:1}\n_[n]um:XXXXXXXXXXX => num:${SAY:0:2}, digits/billion, num:${SAY:2}\n_[n]um:XXXXXXXXXXXX => num:${SAY:0:3}, digits/billion, num:${SAY:3}\n_e[n]um:X => digits/h-${SAY}\n_e[n]um:1X => digits/h-${SAY}\n_e[n]um:[2-9]0 => digits/h-${SAY}\n_e[n]um:[2-9][1-9] => num:${SAY:0:1}0, digits/h-${SAY:1}\n_e[n]um:[1-9]XX => num:${SAY:0:1}, digits/hundred, enum:${SAY:1}')
        f.write("[it](digit-base,date-base)\n_[n]um:0. => num:${SAY:1}\n_[n]um:X => digits/${SAY}\n_[n]um:1X => digits/${SAY}\n_[n]um:[2-9]0 =>  digits/${SAY}\n_[n]um:[2-9][1-9] =>  digits/${SAY:0:1}0, num:${SAY:1}\n_[n]um:1XX => digits/hundred, num:${SAY:1}\n_[n]um:[2-9]XX => num:${SAY:0:1}, digits/hundred, num:${SAY:1}\n_[n]um:1XXX => digits/thousand, num:${SAY:1}\n_[n]um:[2-9]XXX => num:${SAY:0:1}, digits/thousands, num:${SAY:1}\n_[n]um:XXXXX => num:${SAY:0:2}, digits/thousands, num:${SAY:2}\n_[n]um:XXXXXX => num:${SAY:0:3}, digits/thousands, num:${SAY:3}\n_[n]um:1XXXXXX => num:${SAY:0:1}, digits/million, num:${SAY:1}\n_[n]um:[2-9]XXXXXX => num:${SAY:0:1}, digits/millions, num:${SAY:1}\n_[n]um:XXXXXXXX => num:${SAY:0:2}, digits/millions, num:${SAY:2}\n_[n]um:XXXXXXXXX => num:${SAY:0:3}, digits/millions, num:${SAY:3}\n_datetime::. => date:AdBY 'digits/at' IMp:${SAY}\n_date::. => date:AdBY:${SAY}\n_time::. => date:IMp:${SAY}")
        f.write("[en](en-base,date-base,digit-base)\n_datetime::. => date:AdBY 'digits/at' IMp:${SAY}\n_date::. => date:AdBY:${SAY}\n_time::. => date:IMp:${SAY}")
        f.write("[de](date-base,digit-base)\n_[n]um:0. => num:${SAY:1}\n_[n]um:X => digits/${SAY}\n_[n]um:1X => digits/${SAY}\n_[n]um:[2-9]0 => digits/${SAY}\n_[n]um:[2-9][1-9] => digits/${SAY:1}-and, digits/${SAY:0:1}0\n_[n]um:1XX => digits/ein, digits/hundred, num:${SAY:1}\n_[n]um:[2-9]XX => digits/${SAY:0:1}, digits/hundred, num:${SAY:1}\n_[n]um:1XXX => digits/ein, digits/thousand, num:${SAY:1}\n_[n]um:[2-9]XXX => digits/${SAY:0:1}, digits/thousand, num:${SAY:1}\n_[n]um:XXXXX => num:${SAY:0:2}, digits/thousand, num:${SAY:2}\n_[n]um:X00XXX => digits/${SAY:0:1}, digits/hundred, digits/thousand, num:${SAY:3}\n_[n]um:XXXXXX => digits/${SAY:0:1}, digits/hundred, num:${SAY:1}\n_[n]um:1XXXXXX => digits/eine, digits/million, num:${SAY:1}\n_[n]um:[2-9]XXXXXX => digits/${SAY:0:1}, digits/millions, num:${SAY:1}\n_[n]um:XXXXXXXX => num:${SAY:0:2}, digits/millions, num:${SAY:2}\n_[n]um:XXXXXXXXX => num:${SAY:0:3}, digits/millions, num:${SAY:3}\n_datetime::. => date:AdBY 'digits/at' IMp:${SAY}\n_date::. => date:AdBY:${SAY}\n_time::. => date:IMp:${SAY}")
        f.close()

        # sip.conf
        f = open('/usr/local/etc/afelio/sip.conf', 'w')
        # write sections to file in order
        for i in self.config.getVar('svc.voip.sip._index'):
            f.write('['+i+']\n')
            for key, val in self.config.getVars('svc.voip.sip.'+i+'.*').iteritems():
                f.write(key.split('.')[4]+' = '+val+'\n')
        f.close()

        # sip_notify.conf
        f = open('/usr/local/etc/afelio/sip_notify.conf', 'w')
        f.write('[polycom-check-cfg]\nEvent=>check-sync\nContent-Length=>0')
        f.write('[sipura-check-cfg]\nEvent=>resync\nContent-Length=>0')
        f.write('[grandstream-check-cfg]\nEvent=>sys-control')
        f.write('[cisco-check-cfg]\nEvent=>check-sync\nContent-Length=>0')
        f.write('[snom-check-cfg]\nEvent=>check-sync\;reboot=false\nContent-Length=>0')
        f.close()

        # skinny.conf
        f = open('/usr/local/etc/afelio/skinny.conf', 'w')
        f.write('[general]\nbindaddr=0.0.0.0\nbindport=2000\ndateformat=M-D-Y\nkeepalive=120')
        f.close()

        # sla.conf
        f = open('/usr/local/etc/afelio/sla.conf', 'w')
        f.write('[general]')
        f.close()

        # smdi.conf
        f = open('/usr/local/etc/afelio/smdi.conf', 'w')
        f.write('[interfaces]')
        f.close()

        # telcordia-1.adsi
        f = open('/usr/local/etc/afelio/telcordia-1.conf', 'w')
        f.write('DESCRIPTION "Telcordia Demo"\nVERSION 0x02\nSECURITY 0x0000\nFDN 0x0000000f\nDISPLAY "talkingto" IS "Talking To" "$Call1p" WRAP\nDISPLAY "titles" IS "20th Century IQ Svc"\nDISPLAY "newcall" IS "New Call From" "$Call1p" WRAP\nDISPLAY "ringing" IS "Ringing"\nSTATE "callup"\nSTATE "inactive"\nKEY "CB_OH" IS "Block" OR "Call Block"\n\tOFFHOOK\n\tVOICEMODE\n\tWAITDIALTONE\n\tSENDDTMF "*60"\n\tSUBSCRIPT "offHook"\nENDKEY')
        f.write('KEY "CB" IS "Block" OR "Call Block"\n\tSENDDTMF "*60"\nENDKEY')
        f.write('SUB "main" IS\n\tIFEVENT NEARANSWER THEN\n\t\tCLEAR\n\t\tSHOWDISPLAY "talkingto" AT 1\n\t\tGOTO "stableCall"\n\tENDIF\n\tIFEVENT OFFHOOK THEN\n\t\tCLEAR\n\t\tSHOWDISPLAY "titles" AT 1\n\t\tSHOWKEYS "CB"\n\t\tGOTO "offHook"\n\tENDIF\n\tIFEVENT IDLE THEN\n\t\tCLEAR\n\t\tSHOWDISPLAY "titles" AT 1\n\t\tSHOWKEYS "CB_OH"\n\tENDIF\n\tIFEVENT CALLERID THEN\n\t\tCLEAR\n\t\tSHOWDISPLAY "newcall" AT 1\n\tENDIF\nENDSUB')
        f.write('SUB "offHook" IS\n\tIFEVENT FARRING THEN\n\t\tCLEAR\n\t\tSHOWDISPLAY "ringing" AT 1\n\tENDIF\n\tIFEVENT FARANSWER THEN\n\t\tCLEAR\n\t\tSHOWDISPLAY "talkingto" AT 1\n\t\tGOTO "stableCall"\n\tENDIF\nENDSUB')
        f.write('SUB "stableCall" IS\nENDSUB')
        f.close()

        # udptl.conf
        f = open('/usr/local/etc/afelio/udptl.conf', 'w')
        f.write('[general]\nudptlstart=4000\nudptlend=4999\nT38FaxUdpEC = t38UDPFEC\nT38FaxMaxDatagram = 400\nudptlfecentries = 3\nudptlfecspan = 3')
        f.close()

        # users.conf
        f = open('/usr/local/etc/afelio/users.conf', 'w')
        f.write('[general]\nfullname = New User\nuserbase = 1000\nhasvoicemail = yes\nvmsecret = 1234\nhassip = yes\nhasiax = yes\nhash323 = no\nhasmanager = no\ncallwaiting = yes\nthreewaycalling = yes\ncallwaitingcallerid = yes\ntransfer = yes\ncanpark = yes\ncancallforward = yes\ncallreturn = yes\ncallgroup = 1\npickupgroup = 1')
        f.close()

        # voicemail.conf
        f = open('/usr/local/etc/afelio/voicemail.conf', 'w')
        f.write('[general]\nformat=wav49|gsm|wav\nserveremail=afelio\nattach=yes\nskipms=3000\nmaxsilence=10\nsilencethreshold=128\nmaxlogins=3')
        f.write("[zonemessages]\neastern=America/New_York|'vm-received' Q 'digits/at' IMp\ncentral=America/Chicago|'vm-received' Q 'digits/at' IMp\ncentral24=America/Chicago|'vm-received' q 'digits/at' H N 'hours'\nmilitary=Zulu|'vm-received' q 'digits/at' H N 'hours' 'phonetic/z_p'\neuropean=Europe/Copenhagen|'vm-received' a d b 'digits/at' HM")
        f.write('[default]\n1234 => 4242,Example Mailbox,root@localhost')
        f.write('[other]\n1234 => 5678,Company2 User,root@localhost')
        f.close()

        # vpb.conf
        f = open('/usr/local/etc/afelio/vpb.conf', 'w')
        f.write('[general]\ntype = v12pci\ncards = 1')
        f.write('[interfaces]\nboard = 0\nechocancel = on\ncontext = demo\nmode = fxo\nchannel = 8\nchannel = 9\nchannel = 10\nchannel = 11\ncontext = local\nmode = dialtone\nchannel = 0\nchannel = 1\nchannel = 2\nchannel = 3\nchannel = 4\nchannel = 5\nchannel = 6\nchannel = 7')
        f.close()

        # zapata.conf
        f = open('/usr/local/etc/afelio/zapata.conf', 'w')
        # Write sections to file in order
        for i in self.config.getVar('svc.voip.zapata._index'):
            f.write('[%s]\n' % (i))
            if i == 'channels':
                # Currently, the variable "pritimer" isn't supported
                # These are the defaults for all channels
                for key, val in self.config.getVars('svc.voip.zapata.'+i+'.[a-zA-Z]').iteritems():
                    f.write('%s = %s\n' % (key.split('.')[4], val))

                # Write channel information in order
                for channel in self.config.getVar('svc.voip.zapata.'+i+'._index'):
                    for key, val in self.config.getVars('svc.voip.zapata.'+i+'.'+channel).iteritems():
                        f.write('%s = %s\n' % (key.split('.')[5], val))
                    else:
                        f.write('channel => %s\n' % (key.split('.')[4]))
            else:
                for key, val in self.config.getVars('svc.voip.zapata.'+i+'.*').iteritems():
                    f.write('%s => %s\n' % (key.split('.')[4], val))
        f.close()

        # zaptel.conf
        f = open('/usr/local/etc/zaptel.conf', 'w')
        for key, val in self.config.getVars('svc.voip.zaptel.*').iteritems():
            key = key.split('.')[3]
            if type(val) == str:
                f.write(key+'='+val+'\n')
            else:
                for i in val:
                    f.write(key+'='+i+'\n')
        f.close()

        # Run asterisk
        rc = subprocess.call(['/usr/local/sbin/asterisk'])
        return(retVal)

    def stop(self):
        retVal = True
        return(retVal)

    def restart(self):
        retVal = True
        return(retVal)

    def stat(self):
        retVal = True
        return(retVal)

