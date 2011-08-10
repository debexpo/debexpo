#! /usr/bin/perl

# -*- coding: utf-8 -*-
#
#   forge-changes.pl - 
#   Forge a changes file for the mentors -> expo transition
#
#   This file is part of debexpo - http://debexpo.workaround.org
#
#   This file is /so/ ugly code I refuse to declare any authors or
#   copyright on it. Do whatever you want with it! 
#   Perhaps get rid of it, as soon as you don't need it anymore.


use File::Find;
use File::Basename;

our @directories_to_search = ("/tmp/pkg/");
if ($directories_to_search[0] eq '/CHANGE/ME')
{
	die();
}
our @binaries = ( ["sha1sum", "Checksums-Sha1"], ["sha256sum", "Checksums-Sha256"], ["md5sum", "Files"]);
find(\&wanted, @directories_to_search);


sub wanted
{

	my $package = $_;
	if ($File::Find::name !~ /\.dsc/)
	{
		return;
	}
	
	my $changes = $File::Find::name;
	$changes =~ s/\.dsc/_source.changes/;
	my $version;
	my $maintainer;
	my $changed_by;
	my %tarballs;

	if($package =~ m/(.*?)_(.*?)\.dsc/)
	{
		$package = $1;
		$version = $2;
	}
	else
	{
		return;
	}

	open(DSC, "< $File::Find::name") || die "$!";
	while(<DSC>)
	{
		if (/Maintainer:/)
		{
			chomp;
			(undef, $maintainer) = split(/:/, $_, 2);
			($maintainer, undef) = split(/,/, $maintainer, 2)
		}
		if (/Uploaders:/)
		{
			# overwrite maintainer
			chomp;
			(undef, $maintainer) = split(/:/, $_, 2);
			($maintainer, undef) = split(/,/, $maintainer, 2)
		}
		if (/[a-f0-9] \d+? (.*?)$/)
		{
			$archive = $1;
			chomp($archive);
			$tarballs{$archive} = 1;
			#print("--> $archive\n");
		}
	}
	close(DSC);
	$changed_by = $maintainer;
	print("Processing $File::Find::name -> $changes\n");

	open(CH, "> $changes") || die "$1";
	print CH "Format: 1.8\n";
	print CH "Date: Tue, 26 Jul 2011 17:40:04 +0200\n";
	print CH "Source: $package\n";
	print CH "Binary: $package\n";
	print CH "Architecture: source\n";
	print CH "Version: $version\n";
	print CH "Distribution: unstable\n";
	print CH "Urgency: low\n";
	print CH "Maintainer: $maintainer\n";
	print CH "Changed-By: $changed_by\n";
	print CH "Description:\n";
	print CH " $package - Automatically imported during mentors.debian.net migration -- re-upload to get fresh data here\n";
	print CH "Changes:\n";
	print CH " $package ($version) unstable; urgency=low\n";
	print CH " .\n";
	print CH " Changelogs are overrated\n";
	
	foreach $tuple (@binaries)
	{
		print CH "$tuple->[1]:\n";
		print CH checksum($tuple->[0], $File::Find::name, ($tuple->[1] eq "Files") ? 1 : 0);
		foreach $key (keys %tarballs)
		{
            if (! -e $File::Find::dir . "/" . $key )
            {
                print("Incomplete upload " . $File::Find::dir . "/" . $key  . "\n");
                close(CH);
                unlink($changes);
                return;
            }
			print CH checksum($tuple->[0], $File::Find::dir . "/" . $key, ($tuple->[1] eq "Files") ? 1 : 0);
		}
	}

	close(CH);	

}


sub checksum
{
	my ($cmd, $file, $section) = @_;
	#print("$file\n");
	$size = -s $file;
	$r = `$cmd $file`;
	chomp($r);
	($checksum, $file) = split(/ /, $r, 2);
	$file = basename($file);
	if ($section == 0)
	{
		return " $checksum $size $file\n";
	}
	else
	{
		return " $checksum $size web extra $file\n";
	}
}
