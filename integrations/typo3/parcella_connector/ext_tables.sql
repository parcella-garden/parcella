CREATE TABLE tx_parcellaconnector_source (
    uid int(11) unsigned NOT NULL auto_increment,
    source_id varchar(100) DEFAULT '' NOT NULL,
    news_uid int(11) unsigned DEFAULT '0' NOT NULL,
    PRIMARY KEY (uid),
    UNIQUE KEY source_id (source_id)
);
