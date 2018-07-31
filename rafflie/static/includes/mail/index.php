<?php
require 'config.php';

$subject = $_REQUEST['subject'] . ' ' . EMAIL_SUBJECT; // Subject of your email
$to = EMAIL_ADDRESS;
$headers  = 'MIME-Version: 1.0' . "\r\n";
$headers .= "From: " . $_REQUEST['email'] . "\r\n"; // Sender's E-mail
$headers .= 'Content-type: text/html; charset=iso-8859-1' . "\r\n";

$message .= 'Name: ' . $_REQUEST['name'] . "<br>";
$message .= $_REQUEST['message'];

if (email_validate($_REQUEST['email']) && @mail($to, $subject, $message, $headers))
	echo 'sent';
else
	echo 'failed';
?>