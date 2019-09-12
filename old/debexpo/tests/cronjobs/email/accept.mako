Return-Path: <envelope@ftp-master.debian.org>
Delivered-To: vtime@example.org
Received: from mailly.debian.org ([2001:41b8:202:deb:6564:a62:52c3:4b72])
    by example.org with esmtps (TLS1.2:ECDHE_RSA_AES_256_GCM_SHA384:256)
    (Exim 4.92)
    (envelope-from <envelope@ftp-master.debian.org>)
    id 1hoOZz-0006UP-2t
    for vtime@example.org; Fri, 19 Jul 2019 08:49:27 +0000
Received: from fasolo.debian.org ([138.16.160.17])
    from C=NA,ST=NA,L=Ankh Morpork,O=Debian SMTP,OU=Debian SMTP CA,CN=fasolo.debian.org,EMAIL=hostmaster@fasolo.debian.org (verified)
    by mailly.debian.org with esmtps (TLS1.2:ECDHE_RSA_AES_256_GCM_SHA384:256)
    (Exim 4.89)
    (envelope-from <envelope@ftp-master.debian.org>)
    id 1hoOZy-0005eA-4z; Fri, 19 Jul 2019 08:49:26 +0000
Received: from dak by fasolo.debian.org with local (Exim 4.89)
    (envelope-from <envelope@ftp-master.debian.org>)
    id 1hoOZx-000ABa-1I; Fri, 19 Jul 2019 08:49:25 +0000
From: Debian FTP Masters <ftpmaster@ftp-master.debian.org>
To: Vincent TIME <vtime@example.org>
X-DAK: dak process-upload
X-Debian: DAK
X-Debian-Package: ${ c['name'] }
Precedence: bulk
Auto-Submitted: auto-generated
MIME-Version: 1.0
Content-Type: text/plain; charset="utf-8"
Content-Transfer-Encoding: 8bit
Subject: ${ c['name'] }_${ c['version'] }_source.changes ACCEPTED into ${ c['distrib'] }
Message-Id: <E1hoOZx-000ABa-1I@fasolo.debian.org>
Date: Fri, 19 Jul 2019 08:49:25 +0000
Received-SPF: none client-ip=2001:41b8:202:deb:6564:a62:52c3:4b72; envelope-from=envelope@ftp-master.debian.org; helo=mailly.debian.org

Format: 1.8
Date: Tue, 16 Jul 2019 23:37:22 +0200
Source: ${ c['name'] }
Architecture: source
Version: ${ c['version'] }
Distribution: ${ c['distrib'] }
Urgency: medium
Maintainer: Vincent TIME <vtime@example.org>
Changed-By: Vincent TIME <vtime@example.org>
Changes:
 ${ c['name'] } (${ c['version'] }) ${ c['distrib'] }; urgency=medium
 .
   * Rebuild, no changes
Checksums-Sha1:
 36a03fa187774adfbe732dff7a3b23784647a783 1818 ${ c['name'] }_${ c['version'] }.dsc
 c2a9b41fa5052c3248ad338ed39d23f7166213df 5548 ${ c['name'] }_${ c['version'] }.debian.tar.xz
 6e0a0beb343beab28d2e1215fa4c18be2b508ef7 6031 ${ c['name'] }_${ c['version'] }_amd64.buildinfo
Checksums-Sha256:
 63e84b7dc83a8a263b1d0093b7d0b69d15282f4c128cf5f90cef666582ec333e 1818 ${ c['name'] }_${ c['version'] }.dsc
 12ab5db9022e5f470de823656d9706248dcb5793d330e19e3b5178d22d247c91 5548 ${ c['name'] }_${ c['version'] }.debian.tar.xz
 1173147d14de7d56bc1ecf98d2a3616f3348e3a4c055f684306f37d5b98b3bc0 6031 ${ c['name'] }_${ c['version'] }_amd64.buildinfo
Files:
 88619dc01f636b0f180cfc67653b932f 1818 utils optional ${ c['name'] }_${ c['version'] }.dsc
 4e978439dac618e92c982b75f701ddee 5548 utils optional ${ c['name'] }_${ c['version'] }.debian.tar.xz
 461ea7fb0137d8b726787561ea1a8966 6031 utils optional ${ c['name'] }_${ c['version'] }_amd64.buildinfo
