#! /usr/bin/perl
#
# Quick perl script to check simple CSV (really "value" seperated) files
# for some sort of consistency.  All we can really do, is keep the first
# line as a header line, and make sure all following lines have the same
# number of fields.
#
# Current fields/columns in machines.csv:
#   0-4: NAME | ROOM | IP | OS | OS version |
#   5-9: CATEGORY | OWNER | AUTHORITY | BARCODE | DESCRIPTION | 
# 10-14: SPARE1 | SERIAL NUMBER | HOSTID | Host Status | Inventory Status |
# 15-20: Firewall | TrustLevel | RACKINFO | POWER UP | IST TEAM | Comments


die "Need file argument to check: $0 machines.csv\n" if($#ARGV < 0);

$file = shift;
open(FD, "<$file") || die;
chomp($header = <FD>);
@h = split(/\|/, $header);

$i = 2;
while(<FD>){
	$problems = "";
	@a = split(/\|/);
	warn "$file: Wrong number of fields on line $i. ($#a != $#h)\n" if($#a != $#h);

# this needs to be less generic
# some checks, like location (field 1) need additional information like
# the type of device - eg. a VM needs to be correctly "located" on the
# VM server
	# Check individual fields for compliance
	for($j = 0; $j <= $#h; $j++){
		check_field($i, $j, $a[$j]);
	}

	if ($a[2] ne "") {
# should check here if the owner of an alias is in the file
		if ($a[5] ne "alias" && $addrs{$a[2]} ne "") {
			$problems .= "\tduplicate IP $a[2] (seen at $addrs{$a[2]})\n";
		} elsif ($a[5] ne "alias") {
			$addrs{$a[2]} = "$a[0]";
		}
	}

	if ($problems ne "") {
		chomp;
		print "$i $_\n";
		print $problems;
	}

	# Increment record/line number
	$i++;
}
close(FD);

# Checking UUID (with a python script)
system("python3", "check_machines_uuid.py") == 0 or die "Python script returned error $?";


sub check_field {
	my $rn = shift;
	my $fn = shift;
	my $v = shift;

	# Dispatch through field number
	my $e = &{'check_field_'.$fn}($v);
	print 'FAIL '. $h[$fn] .':'. $rn .' "'. $v .'": '. $e .".\n"
		if($e ne '');
};

# name
sub check_field_0 {
	my $v = shift;

	return "must be [a-z0-9_-] only"
		if($v !~ m/^[a-z0-9_-]*$/);
};

# room
sub check_field_1 {
	my $v = shift;
	my %valid = (
		'', 1,
		'ATH101', 1,
		'ATH102', 1,
		'ATH105', 1,
		'ATH106', 1,
		'ATH107', 1,
		'ATH108', 1,
		'ATH109', 1,
		'ATH111', 1,
		'ATH113', 1,
		'ATH117', 1,
		'ATH119', 1,
		'ATH120', 1,
		'ATH121', 1,
		'ATH122', 1,
		'ATH123', 1,
		'ATH124', 1,
		'ATH126', 1,
		'ATH128', 1,
		'ATH129', 1,
		'ATH130', 1,
		'ATH132', 1,
		'ATH133', 1,
		'ATH134', 1,
		'ATH135', 1,
		'ATH136', 1,
		'ATH137', 1,
		'ATH138', 1,
		'ATH139', 1,
		'ATH140', 1,
		'ATH141', 1,
		'ATH143', 1,
		'ATH147', 1,
		'ATH150', 1,
		'ATH151', 1,
		'ATH152', 1,
		'ATH153', 1,
		'ATH154', 1,
		'ATH155', 1,
		'ATH200', 1,
		'ATH201', 1,
		'ATH202', 1,
		'ATH203', 1,
		'ATH204', 1,
		'ATH205', 1,
		'ATH206', 1,
		'ATH207', 1,
		'ATH209', 1,
		'ATH211', 1,
		'ATH215', 1,
		'ATH217', 1,
		'ATH218', 1,
		'ATH219', 1,
		'ATH220', 1,
		'ATH221', 1,
		'ATH224', 1,
		'ATH224A', 1,
		'ATH231', 1,
		'ATH232', 1,
		'ATH233', 1,
		'ATH234', 1,
		'ATH235', 1,
		'ATH236', 1,
		'ATH237', 1,
		'ATH238', 1,
		'ATH241', 1,
		'ATH243', 1,
		'ATH245', 1,
		'ATH252A', 1,
		'ATH252B', 1,
		'ATH252C', 1,
		'ATH252D', 1,
		'ATH252E', 1,
		'ATH252F', 1,
		'ATH301', 1,
		'ATH302', 1,
		'ATH303', 1,
		'ATH304', 1,
		'ATH305', 1,
		'ATH306', 1,
		'ATH307', 1,
		'ATH308', 1,
		'ATH309', 1,
		'ATH311', 1,
		'ATH313', 1,
		'ATH315', 1,
		'ATH317', 1,
		'ATH319', 1,
		'ATH320', 1,
		'ATH321', 1,
		'ATH322', 1,
		'ATH323', 1,
		'ATH324', 1,
		'ATH326', 1,
		'ATH328', 1,
		'ATH329', 1,
		'ATH332', 1,
		'ATH334', 1,
		'ATH335', 1,
		'ATH336', 1,
		'ATH337', 1,
		'ATH338', 1,
		'ATH339', 1,
		'ATH340', 1,
		'ATH341', 1,
		'ATH342', 1,
		'ATH343', 1,
		'ATH345', 1,
		'ATH347', 1,
		'ATH349', 1,
		'ATH351', 1,
		'ATH352', 1,
		'ATH353', 1,
		'ATH354', 1,
		'ATH355', 1,
		'ATH356', 1,
		'ATH357', 1,
		'ATH358', 1,
		'ATH359', 1,
		'ATH401', 1,
		'ATH402', 1,
		'ATH403', 1,
		'ATH404', 1,
		'ATH405', 1,
		'ATH406', 1,
		'ATH407', 1,
		'ATH408', 1,
		'ATH409', 1,
		'ATH411', 1,
		'ATH413', 1,
		'ATH415', 1,
		'ATH417', 1,
		'ATH418', 1,
		'ATH419', 1,
		'ATH420', 1,
		'ATH421', 1,
		'ATH422', 1,
		'ATH423', 1,
		'ATH424', 1,
		'ATH425', 1,
		'ATH427', 1,
		'ATH430', 1,
		'ATH432', 1,
		'ATH434', 1,
		'ATH436', 1,
		'ATH437', 1,
		'ATH438', 1,
		'ATH441', 1,
		'ATH443', 1,
		'ATH445', 1,
		'ATH447', 1,
		'ATH449', 1,
		'ATH450', 1,
		'ATH451', 1,
		'ATH452', 1,
		'CAB311', 1,
		'CAB311A', 1,
		'CSCB21', 1,
		'CSCB23', 1,
		'CSCB31', 1,
		'CSC105', 1,
		'CSC121', 1,
		'CSC123', 1,
		'CSC124', 1,
		'CSC125', 1,
		'CSC129', 1,
		'CSC132', 1,
		'CSC133', 1,
		'CSC135', 1,
		'CSC137', 1,
		'CSC139', 1,
		'CSC140', 1,
		'CSC143', 1,
		'CSC145', 1,
		'CSC147', 1,
		'CSC153', 1,
		'CSC154', 1,
		'CSC159', 1,
		'CSC165', 1,
		'CSC166', 1,
		'CSC167', 1,
		'CSC205', 1,
		'CSC211', 1,
		'CSC211A', 1,
		'CSC215', 1,
		'CSC217', 1,
		'CSC219', 1,
		'CSC218', 1,
		'CSC220', 1,
		'CSC221', 1,
		'CSC224', 1,
		'CSC225', 1,
		'CSC228', 1,
		'CSC229', 1,
		'CSC231', 1,
		'CSC235', 1,
		'CSC241', 1,
		'CSC243', 1,
		'CSC245', 1,
		'CSC247', 1,
		'CSC249', 1,
		'CSC250', 1,
		'CSC252', 1,
		'CSC251', 1,
		'CSC251A', 1,
		'CSC259A', 1,
		'CSC259B', 1,
		'CSC259B1', 1,
		'CSC259B2', 1,
		'CSC259B3', 1,
		'CSC259C', 1,
		'CSC260', 1,
		'CSC261', 1,
		'CSC262', 1,
		'CSC263', 1,
		'CSC265', 1,
		'CSC301', 1,
		'CSC305', 1,
		'CSC305A', 1,
		'CSC311', 1,
		'CSC313', 1,
		'CSC315', 1,
		'CSC315A', 1,
		'CSC319', 1,
		'CSC323', 1,
		'CSC326', 1,
		'CSC327', 1,
		'CSC327A', 1,
		'CSC329', 1,
		'CSC333', 1,
		'CSC341', 1,
		'CSC343', 1,
		'CSC345', 1,
		'CSC347', 1,
		'CSC349', 1,
		'CSC350', 1,
		'CSC351', 1,
		'CSC353', 1,
		'CSC355', 1,
		'CSC357', 1,
		'CSC359', 1,
		'CSC361', 1,
		'CSC363', 1,
		'CSC363A', 1,
		'GSB175', 1,
	);

#	if (! $valid{$v}) {
#		return "must be a valid room, or blank";
#	}
	return;  # always return true until we figure out how to do this test
};

# IP addr
sub check_field_2 {
	my $v = shift;

	return "must be valid IP (w optional /XX subnet), \'nat\', or blank"
		if ($v !~ m/^(((\d{1,3}\.){3}\d{1,3}(\/([1-9]|1[0-9]|2[0-9]|3[0-1]))?)|nat)?$/);
};

# OS
# currently we accept:
# AIX, Linux, MacOS, OpenBSD, SunOS, VMware ESX, Windows, dual-boot,
# or an empty field
# you had better have a really good reason to modify this list
sub check_field_3 {
	my $v = shift;
	my %valid = (
		'', 1,
		'AIX', 1,
		'Linux', 1,
		'MacOS', 1,
		'OpenBSD', 1,
		'SunOS', 1,
		'VMware ESX', 1,
		'Windows', 1,
		'dual-boot', 1,
	);

	return "must be one of: '". join("', '", sort keys %valid) ."'"
		if(! $valid{$v});
};

# OS version
sub check_field_4 {
};

# category
sub check_field_5 {
	my $v = shift;
	my %valid = (
		'', 1,
		'cluster', 1,
		'alias', 1,
		'laptop', 1,
		'network', 1,
		'printer', 1,
		'public', 1,
		'public carp', 1,
		'regular', 1,
		'temporary', 1,
		'unknown', 1,
		'virtual', 1,
		'wildwest', 1,
	);

	return "must be one of: '". join("', '", sort keys %valid) ."'"
		if(! $valid{$v});
};

# owner
sub check_field_6 {
};

# authority
sub check_field_7 {
};

# barcode
sub check_field_8 {
	my $v = shift;
	my %valid = ('', 1, 'NA', 1, 'no-tag', 1);

	return "must be valid UA tag (6 digits) or one of: '". join("', '", sort keys %valid) ."'"
		if(!($valid{$v} || $v =~ m/^\d{6}$/));
};

# description
sub check_field_9 {
};

# unused - spare
sub check_field_10 {
	my $v = shift;

	return 'should be empty'
		if($v ne '');
};

# serial number
sub check_field_11 {
};

# host ID
sub check_field_12 {
};

# host status
sub check_field_13 {
	my $v = shift;
	my %valid = ('', 1, 'NA', 1, 'DIRTY', 1, 'NOP', 1, 'CLEAN', 1);

	return "must be one of: '". join("', '", sort keys %valid) ."'"
		if(! $valid{$v});
};

# inventory status
sub check_field_14 {
	my $v = shift;
	my %valid = (
		'expired', 1,
		'floater', 1,
		'ipalias', 1,
		'surplus', 1,
		'spare', 1,
		'stalled', 1,
		'missing', 1,
		'retired', 1,
		'active', 1,
		'off', 1,
		'temp', 1,
	);

	return "must be one of: '". join("', '", sort keys %valid) ."'"
		if(! $valid{$v});
};

# firewall (?)
sub check_field_15 {
	my $v = shift;
	my %valid = ('', 1, 'NO', 1, 'OK', 1);

	return "must be one of: '". join("', '", sort keys %valid) ."'"
		if(! $valid{$v});
};

# trustlevel (?)
sub check_field_16 {
	my $v = shift;
	my %valid = ('', 1, 'M', 1, 'U', 1, 'T', 1);

	return "must be one of: '". join("', '", sort keys %valid) ."'"
		if(! $valid{$v});
};

# rack info
sub check_field_17 {
	my $v = shift;

	return "must be [A-Z0-9]+, or blank"
		if($v !~ m/^[A-Z\d]*$/);
};

# power up and down
sub check_field_18 {
	my $v = shift;

	return "must be [1-5]"
		if($v !~ m/^[1-5]?$/);
};

# ist team
sub check_field_19 {
	my $v = shift;
	my %valid = ('', 1, 'SA1', 1, 'WPS', 1, 'SRIT', 1,);

	return "must be one of: '". join("', '", sort keys %valid) ."'"
		if(! $valid{$v});
};

# UUID
sub check_field_20 {
};

# comments
sub check_field_21 {
};
