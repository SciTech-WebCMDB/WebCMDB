#! /usr/bin/perl
#
# Quick perl script to check simple CSV (really "value" seperated) files
# for some sort of consistency.  All we can really do, is keep the first
# line as a header line, and make sure all following lines have the same
# number of fields.

die "Need file argument to check: $0 physaddrs.csv\n" if($#ARGV < 0);

# DHCP option patterns for the FLAGS field
# every pattern but the last needs a , after it
@rawoptpats = (
	qr/^filename /,
	qr/^option domain-name-servers /,
	qr/^Always-reply-rfc1048 on/
);
$alloptpats = "(" . join("|", @rawoptpats) . ")";
$optpats = qr/$alloptpats/;

while ($file = shift) {
	open(FD, "<$file") || die;
	chomp($header = <FD>);
	@h = split(/\|/, $header);

	$i = 2;
	while(<FD>){
		@a = split(/\|/);
		chomp($a[$#a]);
		warn "$file: Wrong number of fields on line $i. ($#a != $#h)\n"
			if($#a != $#h);

		# Check individual fields for compliance
		for($j = 0; $j <= $#h; $j++){
			check_field($i, $j, $a[$j]);
		}

		# Increment record/line number
		$i++;
	}
	close(FD);
}

sub check_field {
	my $rn = shift;
	my $fn = shift;
	my $v = shift;

	# Dispatch through field number
	my $e = &{'check_field_'.$fn}($v);
	print 'FAIL '. $h[$fn] .':'. $rn .' "'. $v .'": '. $e .".\n"
		if($e ne '');
};

sub check_field_0 {
	my $v = shift;

	return "must be [a-z][a-z0-9-]* only"
		if($v !~ m/^[a-z][a-z0-9-]*$/);
};

sub check_field_1 {
	my $v = shift;

	return "must be number only"
		if($v !~ m/^\d+$/);
};

sub check_field_2 {
	my $v = shift;

	return "must be valid lower-case MAC"
		if($v !~ m/^([a-f\d]{2}:){5}[a-f\d]{2}$/);
};

sub check_field_3 {
	my $v = shift;

	return "must be a valid IP address"
		if($v !~ m/^(\d+\.){3}\d+$/);
};

sub check_field_4 {
};

sub check_field_5 {
	my $v = shift;

	# empty flags field is allowed
	return if $v =~ /^$/;

	@f = split(/; */, $v, -1);
	foreach $f (@f) {
		return "invalid DHCP option: $f" if ($f !~ $optpats);
	}

	return;
};

