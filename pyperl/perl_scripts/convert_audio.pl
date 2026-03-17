#!/usr/bin/env perl
use strict;
use warnings;

my ($input, $output) = @ARGV;

die "Usage: convert_audio.pl input output\n"
    unless defined $input and defined $output;

system("ffmpeg", "-y", "-i", $input, $output);

if ($? != 0) {
    die "Conversion failed\n";
}

print "Converted $input -> $output\n";