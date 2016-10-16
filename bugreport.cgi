diff -ru a/config/config.php.example b/config/config.php.example
--- a/config/config.php.example	2012-10-01 08:54:14.000000000 +0200
+++ b/config/config.php.example	2016-10-16 20:38:09.469236592 +0200
@@ -379,7 +379,7 @@
 
 /* Default password hashing algorithm. One of md5, ssha, sha, md5crpyt, smd5,
    blowfish, crypt or leave blank for now default algorithm. */
-// $servers->setValue('appearance','password_hash','md5');
+// $servers->setValue('appearance','password_ldap_hash','md5');
 
 /* If you specified 'cookie' or 'session' as the auth_type above, you can
    optionally specify here an attribute to use when logging in. If you enter
@@ -546,7 +546,7 @@
 $servers->setValue('sasl','authz_id_replacement','$1');
 $servers->setValue('sasl','props',null);
 
-$servers->setValue('appearance','password_hash','md5');
+$servers->setValue('appearance','password_ldap_hash','md5');
 $servers->setValue('login','attr','dn');
 $servers->setValue('login','fallback_dn',false);
 $servers->setValue('login','class',null);
Only in b/: file.patch
diff -ru a/lib/PageRender.php b/lib/PageRender.php
--- a/lib/PageRender.php	2012-10-01 08:54:14.000000000 +0200
+++ b/lib/PageRender.php	2016-10-16 20:38:09.377235805 +0200
@@ -287,7 +287,7 @@
 						break;
 
 					default:
-						$vals[$i] = password_hash($passwordvalue,$enc);
+						$vals[$i] = password_ldap_hash($passwordvalue,$enc);
 				}
 
 				$vals = array_unique($vals);
@@ -957,7 +957,7 @@
 		if (trim($val))
 			$enc_type = get_enc_type($val);
 		else
-			$enc_type = $server->getValue('appearance','password_hash');
+			$enc_type = $server->getValue('appearance','password_ldap_hash');
 
 		$obfuscate_password = obfuscate_password_display($enc_type);
 
@@ -982,7 +982,7 @@
 		if (trim($val))
 			$enc_type = get_enc_type($val);
 		else
-			$enc_type = $server->getValue('appearance','password_hash');
+			$enc_type = $server->getValue('appearance','password_ldap_hash');
 
 		echo '<table cellspacing="0" cellpadding="0"><tr><td valign="top">';
 
diff -ru a/lib/TemplateRender.php b/lib/TemplateRender.php
--- a/lib/TemplateRender.php	2012-10-01 08:54:14.000000000 +0200
+++ b/lib/TemplateRender.php	2016-10-16 20:38:09.405236156 +0200
@@ -2466,7 +2466,7 @@
 		if ($val = $attribute->getValue($i))
 			$default = get_enc_type($val);
 		else
-			$default = $this->getServer()->getValue('appearance','password_hash');
+			$default = $this->getServer()->getValue('appearance','password_ldap_hash');
 
 		if (! $attribute->getPostValue())
 			printf('<input type="hidden" name="post_value[%s][]" value="%s" />',$attribute->getName(),$i);
diff -ru a/lib/ds_ldap.php b/lib/ds_ldap.php
--- a/lib/ds_ldap.php	2012-10-01 08:54:14.000000000 +0200
+++ b/lib/ds_ldap.php	2016-10-16 20:41:21.026525871 +0200
@@ -1117,12 +1117,14 @@
 		if (is_array($dn)) {
 			$a = array();
 			foreach ($dn as $key => $rdn)
-				$a[$key] = preg_replace('/\\\([0-9A-Fa-f]{2})/e',"''.chr(hexdec('\\1')).''",$rdn);
+				$a[$key] = preg_replace_callback('/\\\([0-9A-Fa-f]{2})/',
+					function ($matches) { return chr(hexdec($matches[1])); }, $rdn);
 
 			return $a;
 
 		} else
-			return preg_replace('/\\\([0-9A-Fa-f]{2})/e',"''.chr(hexdec('\\1')).''",$dn);
+			return preg_replace_callback('/\\\([0-9A-Fa-f]{2})/',
+					function ($matches) { return chr(hexdec($matches[1])); }, $dn);
 	}
 
 	public function getRootDSE($method=null) {
diff -ru a/lib/ds_ldap_pla.php b/lib/ds_ldap_pla.php
--- a/lib/ds_ldap_pla.php	2012-10-01 08:54:14.000000000 +0200
+++ b/lib/ds_ldap_pla.php	2016-10-16 20:38:09.433236356 +0200
@@ -16,7 +16,7 @@
 	function __construct($index) {
 		parent::__construct($index);
 
-		$this->default->appearance['password_hash'] = array(
+		$this->default->appearance['password_ldap_hash'] = array(
 			'desc'=>'Default HASH to use for passwords',
 			'default'=>'md5');
 
diff -ru a/lib/functions.php b/lib/functions.php
--- a/lib/functions.php	2012-10-01 08:54:14.000000000 +0200
+++ b/lib/functions.php	2016-10-16 20:41:21.030526111 +0200
@@ -2127,7 +2127,7 @@
  *        crypt, ext_des, md5crypt, blowfish, md5, sha, smd5, ssha, sha512, or clear.
  * @return string The hashed password.
  */
-function password_hash($password_clear,$enc_type) {
+function password_ldap_hash($password_clear,$enc_type) {
 	if (DEBUG_ENABLED && (($fargs=func_get_args())||$fargs='NOARGS'))
 		debug_log('Entered (%%)',1,0,__FILE__,__LINE__,__METHOD__,$fargs);
 
@@ -2318,7 +2318,7 @@
 
 		# SHA crypted passwords
 		case 'sha':
-			if (strcasecmp(password_hash($plainpassword,'sha'),'{SHA}'.$cryptedpassword) == 0)
+			if (strcasecmp(password_ldap_hash($plainpassword,'sha'),'{SHA}'.$cryptedpassword) == 0)
 				return true;
 			else
 				return false;
@@ -2327,7 +2327,7 @@
 
 		# MD5 crypted passwords
 		case 'md5':
-			if( strcasecmp(password_hash($plainpassword,'md5'),'{MD5}'.$cryptedpassword) == 0)
+			if( strcasecmp(password_ldap_hash($plainpassword,'md5'),'{MD5}'.$cryptedpassword) == 0)
 				return true;
 			else
 				return false;
@@ -2392,7 +2392,7 @@
 
 		# SHA512 crypted passwords
 		case 'sha512':
-			if (strcasecmp(password_hash($plainpassword,'sha512'),'{SHA512}'.$cryptedpassword) == 0)
+			if (strcasecmp(password_ldap_hash($plainpassword,'sha512'),'{SHA512}'.$cryptedpassword) == 0)
 				return true;
 			else
 				return false;
@@ -2565,12 +2565,14 @@
 		$a = array();
 
 		foreach ($dn as $key => $rdn)
-			$a[$key] = preg_replace('/\\\([0-9A-Fa-f]{2})/e',"''.chr(hexdec('\\1')).''",$rdn);
+			$a[$key] = preg_replace_callback('/\\\([0-9A-Fa-f]{2})/',
+				function ($matches) { return chr(hexdec($matches[1])); }, $rdn );
 
 		return $a;
 
 	} else {
-		return preg_replace('/\\\([0-9A-Fa-f]{2})/e',"''.chr(hexdec('\\1')).''",$dn);
+		return preg_replace_callback('/\\\([0-9A-Fa-f]{2})/',
+				function ($matches) { return chr(hexdec($matches[1])); }, $dn);
 	}
 }
 
Only in b/lib: functions.php.orig
