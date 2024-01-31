-- MySQL dump 10.13  Distrib 5.5.55, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: esyy_frbekbsbbe
-- ------------------------------------------------------
-- Server version	5.6.35-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;



--
-- Table structure for table `fide`
--

DROP TABLE IF EXISTS `fide`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fide` (
  `ID_NUMBER` int(11) NOT NULL,
  `NAME` varchar(32) DEFAULT NULL,
  `TITLE` varchar(3) DEFAULT NULL,
  `COUNTRY` varchar(3) DEFAULT NULL,
  `ELO` int(11) DEFAULT NULL,
  `GAMES` int(11) DEFAULT NULL,
  `BIRTHDAY` date DEFAULT NULL,
  `SEX` varchar(1) DEFAULT NULL,
  `FLAG` varchar(3) DEFAULT NULL,
  `R_ELO` int(11) DEFAULT NULL,
  `B_ELO` int(11) DEFAULT NULL,
  PRIMARY KEY (`ID_NUMBER`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fide`
--

LOCK TABLES `fide` WRITE;
/*!40000 ALTER TABLE `fide` DISABLE KEYS */;
INSERT INTO `fide` VALUES (201308,'Decrop, Ruben','','BEL',1995,1,'1965-04-21','M',NULL,0,0);
INSERT INTO `fide` VALUES (215147,'Decrop, Benjamin','','BEL',2176,2,'1994-05-31','M',NULL,2206,2158);
INSERT INTO `fide` VALUES (215155,'Decrop, Hendrik','','BEL',2120,1,'1999-09-18','M',NULL,2087,0);
INSERT INTO `fide` VALUES (215163,'Decrop, Ronald','','BEL',1691,0,'1935-11-19','M',NULL,0,0);

/*!40000 ALTER TABLE `fide` ENABLE KEYS */;
UNLOCK TABLES;



--
-- Table structure for table `p_player202401`
--

DROP TABLE IF EXISTS `p_player202401`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `p_player202401` (
  `Matricule` int(11) NOT NULL DEFAULT '0',
  `NomPrenom` varchar(32) COLLATE latin1_general_cs DEFAULT NULL,
  `Sexe` char(1) COLLATE latin1_general_cs DEFAULT NULL,
  `Club` mediumint(9) DEFAULT NULL,
  `Dnaiss` date DEFAULT NULL,
  `OldELO` smallint(6) DEFAULT NULL,
  `OldPart` smallint(6) DEFAULT NULL,
  `sELOs` int(11) DEFAULT NULL,
  `Elo` smallint(6) DEFAULT NULL,
  `NbPart` smallint(6) DEFAULT NULL,
  `EloMod` tinyint(4) DEFAULT NULL,
  `Suppress` tinyint(1) DEFAULT NULL,
  `Titre` char(3) COLLATE latin1_general_cs DEFAULT NULL,
  `sPoints` decimal(7,1) DEFAULT NULL,
  `DerJeux` date DEFAULT NULL,
  `Federation` char(2) COLLATE latin1_general_cs DEFAULT NULL,
  `Nat` varchar(4) COLLATE latin1_general_cs DEFAULT NULL,
  `Fide` int(11) DEFAULT NULL,
  `Arbitre` varchar(4) COLLATE latin1_general_cs DEFAULT NULL,
  `NatFide` char(3) COLLATE latin1_general_cs DEFAULT NULL,
  PRIMARY KEY (`Matricule`),
  KEY `NomPrenom` (`NomPrenom`),
  KEY `Club` (`Club`),
  KEY `Dnaiss` (`Dnaiss`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 COLLATE=latin1_general_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `p_player202401`
--

LOCK TABLES `p_player202401` WRITE;
/*!40000 ALTER TABLE `p_player202401` DISABLE KEYS */;
INSERT INTO `p_player202401` VALUES (12394,'Decrop, Ronald','M',901,'1935-11-19',1598,1062,5980,1598,1062,NULL,1,'',3.0,'2019-11-17','F','BEL',215163,'','BEL');
INSERT INTO `p_player202401` VALUES (22826,'Decrop, Evan','M',901,'2007-02-09',0,0,0,0,0,NULL,1,'',0.0,'2020-10-28','','BEL',0,'','');
INSERT INTO `p_player202401` VALUES (28436,'Decrop, Benjamin','M',301,'1994-05-31',2176,862,17949,2178,870,NULL,0,'',3.0,'2023-12-16','V','BEL',215147,'','BEL');
INSERT INTO `p_player202401` VALUES (28908,'Decrop, Hendrik','M',301,'1999-09-18',2083,495,8806,2096,499,NULL,0,'',2.0,'2023-12-03','V','BEL',215155,'','BEL');
INSERT INTO `p_player202401` VALUES (45608,'Decrop, Ruben','M',301,'1965-04-21',1992,974,8189,1997,978,NULL,0,'',2.0,'2023-12-03','V','BEL',201308,'C ','BEL');
/*!40000 ALTER TABLE `p_player202401` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `p_user`
--

DROP TABLE IF EXISTS `p_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `p_user` (
  `user` varchar(20) COLLATE latin1_general_cs NOT NULL DEFAULT '',
  `password` varchar(32) COLLATE latin1_general_cs NOT NULL DEFAULT '',
  `club` smallint(6) unsigned DEFAULT NULL,
  `email` varchar(100) COLLATE latin1_general_cs NOT NULL DEFAULT '',
  `divers` varchar(100) COLLATE latin1_general_cs DEFAULT NULL,
  `RegisterDate` timestamp NULL DEFAULT NULL,
  `LoggedDate` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`user`),
  KEY `club` (`club`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 COLLATE=latin1_general_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `p_user`
--

LOCK TABLES `p_user` WRITE;
/*!40000 ALTER TABLE `p_user` DISABLE KEYS */;
INSERT INTO `p_user` VALUES ('45608','9f6f01d997c07151ffd9de9ef722b668',301,'SIGNALETIQUE',NULL,'2007-09-18 07:36:36','2023-12-23 16:41:29');
/*!40000 ALTER TABLE `p_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `signaletique`
--

DROP TABLE IF EXISTS `signaletique`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `signaletique` (
  `Matricule` int(11) NOT NULL,
  `AnneeAffilie` smallint(4) DEFAULT NULL,
  `Club` mediumint(6) unsigned DEFAULT NULL,
  `Nom` varchar(36) COLLATE latin1_general_cs DEFAULT NULL,
  `Prenom` varchar(24) COLLATE latin1_general_cs DEFAULT NULL,
  `Sexe` char(1) COLLATE latin1_general_cs DEFAULT NULL,
  `Dnaiss` date DEFAULT NULL,
  `LieuNaiss` varchar(48) COLLATE latin1_general_cs DEFAULT NULL,
  `Nationalite` char(3) COLLATE latin1_general_cs DEFAULT 'BEL',
  `NatFIDE` char(3) COLLATE latin1_general_cs DEFAULT 'BEL',
  `Adresse` varchar(48) COLLATE latin1_general_cs DEFAULT NULL,
  `Numero` varchar(8) COLLATE latin1_general_cs DEFAULT NULL,
  `BoitePostale` varchar(8) COLLATE latin1_general_cs DEFAULT NULL,
  `CodePostal` varchar(12) COLLATE latin1_general_cs DEFAULT NULL,
  `Localite` varchar(48) COLLATE latin1_general_cs DEFAULT NULL,
  `Pays` varchar(32) COLLATE latin1_general_cs DEFAULT NULL,
  `Telephone` varchar(24) COLLATE latin1_general_cs DEFAULT NULL,
  `Gsm` varchar(24) COLLATE latin1_general_cs DEFAULT NULL,
  `Fax` varchar(24) COLLATE latin1_general_cs DEFAULT NULL,
  `Email` varchar(48) COLLATE latin1_general_cs DEFAULT NULL,
  `MatFIDE` int(11) DEFAULT NULL,
  `Arbitre` varchar(1) COLLATE latin1_general_cs DEFAULT NULL COMMENT 'Arbitre A B C N(at) F(ide)I(nter)',
  `ArbitreAnnee` smallint(4) DEFAULT NULL,
  `Federation` varchar(1) COLLATE latin1_general_cs DEFAULT NULL,
  `AdrInconnue` tinyint(1) unsigned NOT NULL DEFAULT '0' COMMENT 'TRUE si adresse inconnue',
  `RevuePDF` tinyint(1) unsigned NOT NULL DEFAULT '1',
  `Cotisation` char(1) COLLATE latin1_general_cs DEFAULT NULL COMMENT 'j(eunes) s(enior) ',
  `DateCotisation` date DEFAULT NULL COMMENT 'Date Paiement Cotisation',
  `DateInscription` date DEFAULT NULL,
  `DateAffiliation` date DEFAULT NULL,
  `ClubTransfert` mediumint(6) unsigned NOT NULL DEFAULT '0' COMMENT 'Club de destination si transfert',
  `TransfertOpp` tinyint(1) unsigned NOT NULL DEFAULT '0' COMMENT 'Opposition au transfert',
  `ClubOld` mediumint(6) unsigned NOT NULL DEFAULT '0',
  `FedeOld` varchar(1) COLLATE latin1_general_cs DEFAULT NULL,
  `DemiCotisation` tinyint(1) NOT NULL DEFAULT '0',
  `Note` varchar(200) COLLATE latin1_general_cs DEFAULT NULL,
  `DateModif` date DEFAULT NULL,
  `LoginModif` varchar(20) COLLATE latin1_general_cs DEFAULT NULL,
  `Locked` tinyint(1) NOT NULL DEFAULT '0',
  `NouveauMatricule` int(11) DEFAULT NULL COMMENT 'Recherche d''un nouveau Matricule.',
  `DateTransfert` date DEFAULT NULL,
  `Decede` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `G` tinyint(4) DEFAULT NULL,
  `ArbitreFide` varchar(4) COLLATE latin1_general_cs DEFAULT NULL,
  `ArbitreAnneeFide` smallint(4) DEFAULT NULL,
  PRIMARY KEY (`Matricule`),
  KEY `Club` (`Club`),
  KEY `AnneeAffilie` (`AnneeAffilie`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 COLLATE=latin1_general_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `signaletique`
--

LOCK TABLES `signaletique` WRITE;
/*!40000 ALTER TABLE `signaletique` DISABLE KEYS */;
INSERT INTO `signaletique` VALUES (12394,2020,901,'Decrop','Ronald','M','1935-11-19','Namur','BEL','BEL','Av. du Petit Sart','123','','5100','JAMBES','BEL','081/30.43.80','','','mimieronny@yahoo.fr',215163,'',NULL,'F',0,0,'S',NULL,NULL,'2019-08-30',0,0,901,NULL,0,'','2020-04-06','90964',0,NULL,NULL,1,0,NULL,0);
INSERT INTO `signaletique` VALUES (22826,0,901,'Decrop','Evan','M','2007-02-09','Namur','BEL','BEL','Rue Saint-Denys','75','','5330','SART-BERNARD','BEL','','0470/470829',NULL,'evdec2007@gmail.com',0,NULL,NULL,'',0,1,NULL,NULL,'2020-10-23',NULL,0,0,0,NULL,0,'G2022','2020-10-23','62561',0,NULL,NULL,0,0,NULL,NULL);
INSERT INTO `signaletique` VALUES (28436,2024,301,'Decrop','Benjamin','M','1994-05-31',NULL,'BEL','BEL','N. Lemmensstraat','11','','2650','EDEGEM','BEL','03/4481667','','','',215147,'',0,'V',0,1,'S',NULL,NULL,'2023-09-04',0,0,301,NULL,0,'','2012-09-04','45608',0,NULL,NULL,0,0,NULL,0);
INSERT INTO `signaletique` VALUES (28908,2024,301,'Decrop','Hendrik','M','1999-09-18','','BEL','BEL','N. Lemmensstraat','11','','2650','EDEGEM','BEL','03/4481667','','','',215155,'',0,'V',0,1,'S',NULL,NULL,'2023-09-04',0,0,301,NULL,0,'','2021-07-11','45608',0,NULL,NULL,0,0,NULL,0);
INSERT INTO `signaletique` VALUES (45608,2024,301,'Decrop','Ruben','M','1965-04-21',NULL,'BEL','BEL','N.Lemmensstraat','11','','2650','EDEGEM','BEL','03/4481667','0477/57.13.13','','ruben@decrop.net',201308,'C',NULL,'V',0,1,'S',NULL,NULL,'2023-09-04',0,0,301,NULL,0,'','2009-07-30','45608',0,NULL,NULL,0,0,'F',0);
/*!40000 ALTER TABLE `signaletique` ENABLE KEYS */;
UNLOCK TABLES;


-- Dump completed on 2024-01-23 11:25:03
