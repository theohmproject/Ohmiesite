<?php
$protocol='http';
if (isset($_SERVER['HTTPS']))
  if (strtoupper($_SERVER['HTTPS'])=='ON')
    $protocol='https';

header("location: $protocol://".$_SERVER['HTTP_HOST']."/");
?>