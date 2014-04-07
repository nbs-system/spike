

vtemplate_seeds = {

  'naxsi_score'         : ["$SQL", "$RFI", "$TRAVERSAL", "$EVADE", "$XSS", "$UWA", "$ATTACK"],
  'naxsi_mz'            : ["BODY", "ARGS", "HEADERS", "FILE_EXT", 
                              "$HEADERS_VAR:Cookie", "$HEADERS_VAR:Content-Type", "$HEADERS_VAR:User-Agent", 
                              "$HEADERS_VAR:Accept-Encoding", "$HEADERS_VAR:Connection"], 

}

rulesets_seeds = {
  'WEB_SERVER'  : 'web_server.rules', 
  'APP_SERVER'  : 'app_server.rules', 
  'WEB_APPS'    : 'web_apps.rules', 
  'SCANNER'     : 'scanner_rules',
  'MALWARE'     : 'malware_rules',

  }

settings_seeds = {

  'rules_export_dir': 'exports', 
  'rules_offset'    : '200000',  
  'backup_dir'      : 'backups', 


}

ruleset_header = """
##########################################################################
#
# doxi_rulesets - rules fo nginx+naxsi
# desc      : %s
# file      : %s
# created   : %s
# by        : nginx-goodies
# download  : https://bitbucket.org/lazy_dogtown/doxi-rules
#
###########################################################################

"""

allowed_chars = "abcdefghijklmnopqrstuvwyzABCDEFGHIJKLMNOPQRSTUVWYZ1234567890-"
