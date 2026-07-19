-- MariaDB dump 10.19  Distrib 10.6.7-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: webikf
-- ------------------------------------------------------
-- Server version	10.6.7-MariaDB-2ubuntu1.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=113 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add lang',7,'add_lang'),(26,'Can change lang',7,'change_lang'),(27,'Can delete lang',7,'delete_lang'),(28,'Can view lang',7,'view_lang'),(29,'Can add navbar',8,'add_navbar'),(30,'Can change navbar',8,'change_navbar'),(31,'Can delete navbar',8,'delete_navbar'),(32,'Can view navbar',8,'view_navbar'),(33,'Can add master labels',9,'add_masterlabels'),(34,'Can change master labels',9,'change_masterlabels'),(35,'Can delete master labels',9,'delete_masterlabels'),(36,'Can view master labels',9,'view_masterlabels'),(37,'Can add home images',10,'add_homeimages'),(38,'Can change home images',10,'change_homeimages'),(39,'Can delete home images',10,'delete_homeimages'),(40,'Can view home images',10,'view_homeimages'),(41,'Can add home banner',11,'add_homebanner'),(42,'Can change home banner',11,'change_homebanner'),(43,'Can delete home banner',11,'delete_homebanner'),(44,'Can view home banner',11,'view_homebanner'),(45,'Can add about us',12,'add_aboutus'),(46,'Can change about us',12,'change_aboutus'),(47,'Can delete about us',12,'delete_aboutus'),(48,'Can view about us',12,'view_aboutus'),(49,'Can add winners',13,'add_winners'),(50,'Can change winners',13,'change_winners'),(51,'Can delete winners',13,'delete_winners'),(52,'Can view winners',13,'view_winners'),(53,'Can add partners',14,'add_partners'),(54,'Can change partners',14,'change_partners'),(55,'Can delete partners',14,'delete_partners'),(56,'Can view partners',14,'view_partners'),(57,'Can add initiatives',15,'add_initiatives'),(58,'Can change initiatives',15,'change_initiatives'),(59,'Can delete initiatives',15,'delete_initiatives'),(60,'Can view initiatives',15,'view_initiatives'),(61,'Can add buttons_ik f_fo r_all',16,'add_buttons_ikf_for_all'),(62,'Can change buttons_ik f_fo r_all',16,'change_buttons_ikf_for_all'),(63,'Can delete buttons_ik f_fo r_all',16,'delete_buttons_ikf_for_all'),(64,'Can view buttons_ik f_fo r_all',16,'view_buttons_ikf_for_all'),(65,'Can add photos_ik f_fo r_all',17,'add_photos_ikf_for_all'),(66,'Can change photos_ik f_fo r_all',17,'change_photos_ikf_for_all'),(67,'Can delete photos_ik f_fo r_all',17,'delete_photos_ikf_for_all'),(68,'Can view photos_ik f_fo r_all',17,'view_photos_ikf_for_all'),(69,'Can add news',18,'add_news'),(70,'Can change news',18,'change_news'),(71,'Can delete news',18,'delete_news'),(72,'Can view news',18,'view_news'),(73,'Can add tab',19,'add_tab'),(74,'Can change tab',19,'change_tab'),(75,'Can delete tab',19,'delete_tab'),(76,'Can view tab',19,'view_tab'),(77,'Can add sub tab',20,'add_subtab'),(78,'Can change sub tab',20,'change_subtab'),(79,'Can delete sub tab',20,'delete_subtab'),(80,'Can view sub tab',20,'view_subtab'),(81,'Can add test',21,'add_test'),(82,'Can change test',21,'change_test'),(83,'Can delete test',21,'delete_test'),(84,'Can view test',21,'view_test'),(85,'Can add about trials_ banner photo',22,'add_abouttrials_bannerphoto'),(86,'Can change about trials_ banner photo',22,'change_abouttrials_bannerphoto'),(87,'Can delete about trials_ banner photo',22,'delete_abouttrials_bannerphoto'),(88,'Can view about trials_ banner photo',22,'view_abouttrials_bannerphoto'),(89,'Can add about trials_ tabs',23,'add_abouttrials_tabs'),(90,'Can change about trials_ tabs',23,'change_abouttrials_tabs'),(91,'Can delete about trials_ tabs',23,'delete_abouttrials_tabs'),(92,'Can view about trials_ tabs',23,'view_abouttrials_tabs'),(93,'Can add about trials_ bottom',24,'add_abouttrials_bottom'),(94,'Can change about trials_ bottom',24,'change_abouttrials_bottom'),(95,'Can delete about trials_ bottom',24,'delete_abouttrials_bottom'),(96,'Can view about trials_ bottom',24,'view_abouttrials_bottom'),(97,'Can add about trials_ feature',25,'add_abouttrials_feature'),(98,'Can change about trials_ feature',25,'change_abouttrials_feature'),(99,'Can delete about trials_ feature',25,'delete_abouttrials_feature'),(100,'Can view about trials_ feature',25,'view_abouttrials_feature'),(101,'Can add season1_ feature',26,'add_season1_feature'),(102,'Can change season1_ feature',26,'change_season1_feature'),(103,'Can delete season1_ feature',26,'delete_season1_feature'),(104,'Can view season1_ feature',26,'view_season1_feature'),(105,'Can add season1_ tabs',27,'add_season1_tabs'),(106,'Can change season1_ tabs',27,'change_season1_tabs'),(107,'Can delete season1_ tabs',27,'delete_season1_tabs'),(108,'Can view season1_ tabs',27,'view_season1_tabs'),(109,'Can add season1_ bottom',28,'add_season1_bottom'),(110,'Can change season1_ bottom',28,'change_season1_bottom'),(111,'Can delete season1_ bottom',28,'delete_season1_bottom'),(112,'Can view season1_ bottom',28,'view_season1_bottom');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$320000$ccZvSDjRXvxIQoVBC6Pw1R$opRp7R5uV/7Gv9ky1LRnVhtyPTZWmloNDnuLOie00q0=','2022-08-29 06:50:31.859594',1,'shubham','','','shubham.thakur3232@gmail.com',1,1,'2022-08-29 06:32:23.521506');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=178 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2022-08-29 06:36:28.447613','eng','Lang object (eng)',1,'[{\"added\": {}}]',7,1),(2,'2022-08-29 06:36:33.322006','1','HomeBanner object (1)',1,'[{\"added\": {}}]',11,1),(3,'2022-08-29 06:38:21.607580','1','HomeBanner object (1)',2,'[{\"changed\": {\"fields\": [\"Pic\"]}}]',11,1),(4,'2022-08-29 06:52:18.736462','en','Lang object (en)',1,'[{\"added\": {}}]',7,1),(5,'2022-08-29 06:52:20.868186','2','HomeBanner object (2)',1,'[{\"added\": {}}]',11,1),(6,'2022-08-29 06:53:50.625436','2','HomeBanner object (2)',2,'[{\"changed\": {\"fields\": [\"Pic\"]}}]',11,1),(7,'2022-08-29 07:35:14.050261','1','MasterLabels object (1)',1,'[{\"added\": {}}]',9,1),(8,'2022-08-29 07:44:58.229462','2','HomeBanner object (2)',2,'[{\"changed\": {\"fields\": [\"Size\"]}}]',11,1),(9,'2022-08-29 08:35:51.497586','1','HomeBanner object (1)',2,'[{\"changed\": {\"fields\": [\"Pic\", \"Language21\", \"Attr1\", \"Attr2\", \"Attr3\", \"Attr4\"]}}]',11,1),(10,'2022-08-29 08:36:02.019684','2','HomeBanner object (2)',2,'[{\"changed\": {\"fields\": [\"Pic\"]}}]',11,1),(11,'2022-08-29 08:37:56.613540','3','HomeBanner object (3)',1,'[{\"added\": {}}]',11,1),(12,'2022-08-29 08:38:31.077726','3','HomeBanner object (3)',2,'[{\"changed\": {\"fields\": [\"Pic\"]}}]',11,1),(13,'2022-08-29 08:38:56.950732','3','HomeBanner object (3)',2,'[{\"changed\": {\"fields\": [\"Pic\"]}}]',11,1),(14,'2022-08-29 08:44:43.781409','3','HomeBanner object (3)',2,'[{\"changed\": {\"fields\": [\"Pic\"]}}]',11,1),(15,'2022-08-29 08:45:35.043305','3','HomeBanner object (3)',2,'[{\"changed\": {\"fields\": [\"Pic\"]}}]',11,1),(16,'2022-08-29 08:48:22.835320','4','HomeBanner object (4)',1,'[{\"added\": {}}]',11,1),(17,'2022-08-29 08:48:35.867114','4','HomeBanner object (4)',2,'[{\"changed\": {\"fields\": [\"Pic\"]}}]',11,1),(18,'2022-08-29 12:11:19.965460','2','MasterLabels object (2)',1,'[{\"added\": {}}]',9,1),(19,'2022-08-29 12:16:42.963292','1','AboutUs object (1)',1,'[{\"added\": {}}]',12,1),(20,'2022-08-29 12:17:30.535887','1','AboutUs object (1)',2,'[{\"changed\": {\"fields\": [\"Pic\"]}}]',12,1),(21,'2022-08-29 12:30:31.489723','3','MasterLabels object (3)',1,'[{\"added\": {}}]',9,1),(22,'2022-08-29 12:31:00.150989','3','MasterLabels object (3)',2,'[{\"changed\": {\"fields\": [\"Label\"]}}]',9,1),(23,'2022-08-29 12:32:11.163727','4','MasterLabels object (4)',1,'[{\"added\": {}}]',9,1),(24,'2022-08-29 12:34:15.412298','5','MasterLabels object (5)',1,'[{\"added\": {}}]',9,1),(25,'2022-08-29 12:38:14.453241','6','MasterLabels object (6)',1,'[{\"added\": {}}]',9,1),(26,'2022-08-30 03:18:11.482251','1','HomeBanner object (1)',2,'[{\"changed\": {\"fields\": [\"Size\", \"Name\", \"Heading 1\", \"Heading 2 colored\", \"Description\", \"Button1 text\"]}}]',11,1),(27,'2022-08-30 03:18:40.154071','1','HomeBanner object (1)',2,'[{\"changed\": {\"fields\": [\"Keydata\", \"Button1 text\", \"Button2 text\"]}}]',11,1),(28,'2022-08-30 03:20:15.528439','2','HomeBanner object (2)',2,'[{\"changed\": {\"fields\": [\"Keydata\", \"Name\", \"Heading 1\", \"Heading 2 colored\", \"Description\", \"Button1 text\", \"Button2 text\"]}}]',11,1),(29,'2022-08-30 03:20:28.511899','1','HomeBanner object (1)',2,'[{\"changed\": {\"fields\": [\"Keydata\"]}}]',11,1),(30,'2022-08-30 03:21:22.335598','3','HomeBanner object (3)',2,'[{\"changed\": {\"fields\": [\"Keydata\", \"Name\", \"Heading 1\", \"Heading 2 colored\", \"Description\", \"Button1 text\", \"Button2 text\"]}}]',11,1),(31,'2022-08-30 03:22:09.063564','4','HomeBanner object (4)',2,'[{\"changed\": {\"fields\": [\"Keydata\", \"Name\", \"Heading 1\", \"Heading 2 colored\", \"Description\"]}}]',11,1),(32,'2022-08-30 03:46:59.893030','1','AboutUs object (1)',2,'[{\"changed\": {\"fields\": [\"Paragraph 1\", \"Paragraph 2\"]}}]',12,1),(33,'2022-08-30 03:55:17.428967','1','AboutUs object (1)',2,'[{\"changed\": {\"fields\": [\"Pic 2\", \"Pic 3\", \"Pic 4\"]}}]',12,1),(34,'2022-08-30 03:57:08.795489','1','AboutUs object (1)',2,'[{\"changed\": {\"fields\": [\"Paragraph 2\"]}}]',12,1),(35,'2022-08-30 03:57:38.820647','1','AboutUs object (1)',2,'[{\"changed\": {\"fields\": [\"Paragraph 2\"]}}]',12,1),(36,'2022-08-30 04:04:27.527575','4','MasterLabels object (4)',2,'[{\"changed\": {\"fields\": [\"Label\"]}}]',9,1),(37,'2022-08-30 04:09:09.852447','5','MasterLabels object (5)',2,'[{\"changed\": {\"fields\": [\"Label\"]}}]',9,1),(38,'2022-08-30 04:34:08.338813','1','MasterLabels object (1)',2,'[{\"changed\": {\"fields\": [\"Keydata\", \"Label\"]}}]',9,1),(39,'2022-08-30 04:35:04.592178','2','MasterLabels object (2)',2,'[{\"changed\": {\"fields\": [\"Keydata\", \"Label\", \"Extrainfo\"]}}]',9,1),(40,'2022-08-30 04:35:39.018950','3','MasterLabels object (3)',2,'[{\"changed\": {\"fields\": [\"Keydata\", \"Label\", \"Extrainfo\"]}}]',9,1),(41,'2022-08-30 04:36:41.253568','4','MasterLabels object (4)',2,'[{\"changed\": {\"fields\": [\"Keydata\", \"Label\", \"Extrainfo\"]}}]',9,1),(42,'2022-08-30 04:37:29.840255','5','MasterLabels object (5)',2,'[{\"changed\": {\"fields\": [\"Keydata\", \"Label\", \"Extrainfo\"]}}]',9,1),(43,'2022-08-30 04:42:04.887257','1','AboutUs object (1)',2,'[]',12,1),(44,'2022-08-30 04:47:54.785654','1','AboutUs object (1)',2,'[{\"changed\": {\"fields\": [\"Pic 1\"]}}]',12,1),(45,'2022-08-30 04:49:51.900437','1','AboutUs object (1)',2,'[{\"changed\": {\"fields\": [\"Pic 2\", \"Pic 3\"]}}]',12,1),(46,'2022-08-30 04:49:58.883668','1','AboutUs object (1)',2,'[]',12,1),(47,'2022-08-30 04:50:59.779409','1','AboutUs object (1)',2,'[{\"changed\": {\"fields\": [\"Pic 2\"]}}]',12,1),(48,'2022-08-30 04:53:03.801989','6','MasterLabels object (6)',2,'[{\"changed\": {\"fields\": [\"Keydata\", \"Label\", \"Extrainfo\"]}}]',9,1),(49,'2022-08-30 04:53:45.056580','6','MasterLabels object (6)',2,'[{\"changed\": {\"fields\": [\"Label\"]}}]',9,1),(50,'2022-08-30 04:54:56.020455','7','MasterLabels object (7)',1,'[{\"added\": {}}]',9,1),(51,'2022-08-30 04:56:11.351436','8','MasterLabels object (8)',1,'[{\"added\": {}}]',9,1),(52,'2022-08-30 05:26:27.811633','1','Winners object (1)',1,'[{\"added\": {}}]',13,1),(53,'2022-08-30 05:52:26.880834','2','Winners object (2)',1,'[{\"added\": {}}]',13,1),(54,'2022-08-30 05:53:19.679136','1','Winners object (1)',3,'',13,1),(55,'2022-08-30 06:36:59.714531','1','HomeBanner object (1)',2,'[{\"changed\": {\"fields\": [\"Pic\"]}}]',11,1),(56,'2022-08-30 06:37:39.718938','1','HomeBanner object (1)',2,'[{\"changed\": {\"fields\": [\"Pic\"]}}]',11,1),(57,'2022-08-30 06:38:09.588785','2','HomeBanner object (2)',2,'[{\"changed\": {\"fields\": [\"Pic\"]}}]',11,1),(58,'2022-08-30 06:38:29.279032','3','HomeBanner object (3)',2,'[{\"changed\": {\"fields\": [\"Pic\"]}}]',11,1),(59,'2022-08-30 06:38:40.406061','4','HomeBanner object (4)',2,'[{\"changed\": {\"fields\": [\"Pic\"]}}]',11,1),(60,'2022-08-30 07:20:06.798353','3','Winners object (3)',1,'[{\"added\": {}}]',13,1),(61,'2022-08-30 07:23:42.018290','3','Winners object (3)',2,'[{\"changed\": {\"fields\": [\"Pic\"]}}]',13,1),(62,'2022-08-30 07:30:05.983460','2','Winners object (2)',2,'[{\"changed\": {\"fields\": [\"Name\", \"Pic\"]}}]',13,1),(63,'2022-08-30 07:31:09.890821','4','Winners object (4)',1,'[{\"added\": {}}]',13,1),(64,'2022-08-30 07:31:57.903321','5','Winners object (5)',1,'[{\"added\": {}}]',13,1),(65,'2022-08-30 07:32:31.353097','4','Winners object (4)',2,'[{\"changed\": {\"fields\": [\"Pic\"]}}]',13,1),(66,'2022-08-30 07:57:44.927071','1','Partners object (1)',1,'[{\"added\": {}}]',14,1),(67,'2022-08-30 07:58:31.952928','2','Partners object (2)',1,'[{\"added\": {}}]',14,1),(68,'2022-08-30 07:59:32.722404','3','Partners object (3)',1,'[{\"added\": {}}]',14,1),(69,'2022-08-30 08:00:24.438802','4','Partners object (4)',1,'[{\"added\": {}}]',14,1),(70,'2022-08-30 08:02:29.204329','5','Partners object (5)',1,'[{\"added\": {}}]',14,1),(71,'2022-08-30 08:03:47.048835','5','Partners object (5)',3,'',14,1),(72,'2022-08-30 08:04:48.746646','9','MasterLabels object (9)',1,'[{\"added\": {}}]',9,1),(73,'2022-08-30 08:19:51.067806','1','Initiatives object (1)',1,'[{\"added\": {}}]',15,1),(74,'2022-08-30 08:26:49.876894','1','Initiatives object (1)',2,'[]',15,1),(75,'2022-08-30 08:29:39.171450','1','Initiatives object (1)',2,'[{\"changed\": {\"fields\": [\"Size\"]}}]',15,1),(76,'2022-08-30 08:30:54.769381','2','Initiatives object (2)',1,'[{\"added\": {}}]',15,1),(77,'2022-08-30 08:33:00.392944','3','Initiatives object (3)',1,'[{\"added\": {}}]',15,1),(78,'2022-08-30 08:33:35.026528','4','Initiatives object (4)',1,'[{\"added\": {}}]',15,1),(79,'2022-08-30 08:35:01.012416','10','MasterLabels object (10)',1,'[{\"added\": {}}]',9,1),(80,'2022-08-30 09:02:34.753679','1','Buttons_IKF_FOR_ALL object (1)',1,'[{\"added\": {}}]',16,1),(81,'2022-08-30 09:03:23.866490','2','Buttons_IKF_FOR_ALL object (2)',1,'[{\"added\": {}}]',16,1),(82,'2022-08-30 09:03:53.031051','3','Buttons_IKF_FOR_ALL object (3)',1,'[{\"added\": {}}]',16,1),(83,'2022-08-30 09:04:16.556930','4','Buttons_IKF_FOR_ALL object (4)',1,'[{\"added\": {}}]',16,1),(84,'2022-08-30 09:04:39.439713','5','Buttons_IKF_FOR_ALL object (5)',1,'[{\"added\": {}}]',16,1),(85,'2022-08-30 09:05:22.914507','6','Buttons_IKF_FOR_ALL object (6)',1,'[{\"added\": {}}]',16,1),(86,'2022-08-30 09:05:43.817142','7','Buttons_IKF_FOR_ALL object (7)',1,'[{\"added\": {}}]',16,1),(87,'2022-08-30 09:26:23.733394','1','Photos_IKF_FOR_ALL object (1)',1,'[{\"added\": {}}]',17,1),(88,'2022-08-30 09:30:55.867588','2','Photos_IKF_FOR_ALL object (2)',1,'[{\"added\": {}}]',17,1),(89,'2022-08-30 10:18:29.457255','1','Photos_IKF_FOR_ALL object (1)',3,'',17,1),(90,'2022-08-30 10:18:55.388493','3','Photos_IKF_FOR_ALL object (3)',1,'[{\"added\": {}}]',17,1),(91,'2022-08-30 10:19:13.307327','2','Photos_IKF_FOR_ALL object (2)',2,'[{\"changed\": {\"fields\": [\"Pic\"]}}]',17,1),(92,'2022-08-30 10:19:39.677830','4','Photos_IKF_FOR_ALL object (4)',1,'[{\"added\": {}}]',17,1),(93,'2022-08-30 10:20:22.149926','5','Photos_IKF_FOR_ALL object (5)',1,'[{\"added\": {}}]',17,1),(94,'2022-08-30 10:20:42.043855','4','Photos_IKF_FOR_ALL object (4)',2,'[{\"changed\": {\"fields\": [\"Pic\"]}}]',17,1),(95,'2022-08-30 10:21:29.056066','6','Photos_IKF_FOR_ALL object (6)',1,'[{\"added\": {}}]',17,1),(96,'2022-08-30 10:21:51.071611','7','Photos_IKF_FOR_ALL object (7)',1,'[{\"added\": {}}]',17,1),(97,'2022-08-30 10:22:17.350192','8','Photos_IKF_FOR_ALL object (8)',1,'[{\"added\": {}}]',17,1),(98,'2022-08-30 10:22:45.136283','9','Photos_IKF_FOR_ALL object (9)',1,'[{\"added\": {}}]',17,1),(99,'2022-08-30 10:24:06.090007','11','MasterLabels object (11)',1,'[{\"added\": {}}]',9,1),(100,'2022-08-30 10:56:23.189107','1','News object (1)',1,'[{\"added\": {}}]',18,1),(101,'2022-08-30 10:59:49.222940','2','News object (2)',1,'[{\"added\": {}}]',18,1),(102,'2022-08-30 12:29:23.447462','Home','Tab object (Home)',1,'[{\"added\": {}}]',19,1),(103,'2022-08-30 12:34:09.827152','test','Tab object (test)',1,'[{\"added\": {}}]',19,1),(104,'2022-08-31 05:30:51.728425','test','Tab object (test)',3,'',19,1),(105,'2022-08-31 08:34:49.327445','test','Tab object (test)',2,'[{\"changed\": {\"fields\": [\"Id\", \"Tab\", \"Extra\"]}}]',19,1),(106,'2022-08-31 08:35:03.029958','test','Tab object (test)',3,'',19,1),(107,'2022-08-31 08:52:34.751857','1','MasterLabels object (1)',2,'[]',9,1),(108,'2022-08-31 08:52:44.187567','1','MasterLabels object (1)',2,'[{\"changed\": {\"fields\": [\"Label\"]}}]',9,1),(109,'2022-08-31 08:53:00.845277','1','MasterLabels object (1)',2,'[{\"changed\": {\"fields\": [\"Label\"]}}]',9,1),(110,'2022-08-31 09:15:47.371706','1','MasterLabels object (1)',2,'[]',9,1),(111,'2022-09-01 05:38:24.184831','1','HomeBanner object (1)',2,'[{\"changed\": {\"fields\": [\"Attr1\", \"Attr2\"]}}]',11,1),(112,'2022-09-01 05:39:53.512330','1','HomeBanner object (1)',2,'[{\"changed\": {\"fields\": [\"Attr1\", \"Attr2\"]}}]',11,1),(113,'2022-09-01 05:40:07.110201','2','HomeBanner object (2)',2,'[{\"changed\": {\"fields\": [\"Attr1\"]}}]',11,1),(114,'2022-09-01 05:40:15.785151','3','HomeBanner object (3)',2,'[{\"changed\": {\"fields\": [\"Attr1\"]}}]',11,1),(115,'2022-09-01 05:40:17.941122','3','HomeBanner object (3)',2,'[]',11,1),(116,'2022-09-01 05:40:26.448851','4','HomeBanner object (4)',2,'[{\"changed\": {\"fields\": [\"Attr1\"]}}]',11,1),(117,'2022-09-01 07:04:34.823759','12','MasterLabels object (12)',1,'[{\"added\": {}}]',9,1),(118,'2022-09-01 07:05:50.262556','12','MasterLabels object (12)',2,'[{\"changed\": {\"fields\": [\"Keydata\"]}}]',9,1),(119,'2022-09-01 07:08:13.908089','13','MasterLabels object (13)',1,'[{\"added\": {}}]',9,1),(120,'2022-09-01 07:14:01.138264','1','AboutTrials_BannerPhoto object (1)',1,'[{\"added\": {}}]',22,1),(121,'2022-09-01 07:38:51.431049','1','AboutTrials_BannerPhoto object (1)',2,'[{\"changed\": {\"fields\": [\"Pic\"]}}]',22,1),(122,'2022-09-01 07:39:22.525368','2','AboutTrials_BannerPhoto object (2)',1,'[{\"added\": {}}]',22,1),(123,'2022-09-01 07:41:39.032028','1','AboutTrials_BannerPhoto object (1)',3,'',22,1),(124,'2022-09-01 07:41:41.898592','2','AboutTrials_BannerPhoto object (2)',3,'',22,1),(125,'2022-09-01 07:41:57.405994','3','AboutTrials_BannerPhoto object (3)',1,'[{\"added\": {}}]',22,1),(126,'2022-09-01 08:27:26.046511','1','AboutTrials_Tabs object (1)',1,'[{\"added\": {}}]',23,1),(127,'2022-09-01 08:27:59.918021','2','AboutTrials_Tabs object (2)',1,'[{\"added\": {}}]',23,1),(128,'2022-09-01 09:32:14.692162','1','AboutTrials_Bottom object (1)',1,'[{\"added\": {}}]',24,1),(129,'2022-09-01 09:33:35.043332','2','AboutTrials_Bottom object (2)',1,'[{\"added\": {}}]',24,1),(130,'2022-09-01 09:45:36.408775','14','MasterLabels object (14)',1,'[{\"added\": {}}]',9,1),(131,'2022-09-01 09:47:13.003708','14','MasterLabels object (14)',2,'[{\"changed\": {\"fields\": [\"Extrainfo\"]}}]',9,1),(132,'2022-09-01 09:48:46.274224','15','MasterLabels object (15)',1,'[{\"added\": {}}]',9,1),(133,'2022-09-01 09:49:34.042514','15','MasterLabels object (15)',2,'[]',9,1),(134,'2022-09-01 09:50:11.613957','15','MasterLabels object (15)',3,'',9,1),(135,'2022-09-01 09:50:34.218177','16','MasterLabels object (16)',1,'[{\"added\": {}}]',9,1),(136,'2022-09-01 10:02:56.923914','2','AboutTrials_Bottom object (2)',3,'',24,1),(137,'2022-09-01 10:11:12.927779','1','AboutTrials_Feature object (1)',1,'[{\"added\": {}}]',25,1),(138,'2022-09-01 10:14:09.078609','1','HomeImages object (1)',1,'[{\"added\": {}}]',10,1),(139,'2022-09-01 10:14:21.944550','1','HomeImages object (1)',3,'',10,1),(140,'2022-09-01 16:33:03.677996','17','MasterLabels object (17)',1,'[{\"added\": {}}]',9,1),(141,'2022-09-01 16:33:20.537649','17','MasterLabels object (17)',2,'[{\"changed\": {\"fields\": [\"Label\"]}}]',9,1),(142,'2022-09-01 16:58:55.970648','2','AboutTrials_Feature object (2)',1,'[{\"added\": {}}]',25,1),(143,'2022-09-01 16:59:35.523621','3','AboutTrials_Bottom object (3)',1,'[{\"added\": {}}]',24,1),(144,'2022-09-08 10:09:09.768386','18','MasterLabels object (18)',1,'[{\"added\": {}}]',9,1),(145,'2022-09-08 10:10:09.433857','19','MasterLabels object (19)',1,'[{\"added\": {}}]',9,1),(146,'2022-09-08 10:10:59.065349','20','MasterLabels object (20)',1,'[{\"added\": {}}]',9,1),(147,'2022-09-08 10:11:46.720253','21','MasterLabels object (21)',1,'[{\"added\": {}}]',9,1),(148,'2022-09-08 10:21:36.962074','1','Season1_Feature object (1)',1,'[{\"added\": {}}]',26,1),(149,'2022-09-08 10:27:15.752634','1','Season1_Tabs object (1)',1,'[{\"added\": {}}]',27,1),(150,'2022-09-08 10:29:26.472471','1','Season1_Tabs object (1)',2,'[{\"changed\": {\"fields\": [\"Name\"]}}]',27,1),(151,'2022-09-08 10:29:56.564117','1','Season1_Tabs object (1)',2,'[{\"changed\": {\"fields\": [\"Keydata\", \"Name\"]}}]',27,1),(152,'2022-09-08 10:30:14.647932','1','Season1_Tabs object (1)',2,'[{\"changed\": {\"fields\": [\"Keydata\", \"Name\"]}}]',27,1),(153,'2022-09-08 10:30:38.783737','2','Season1_Tabs object (2)',1,'[{\"added\": {}}]',27,1),(154,'2022-09-08 10:31:15.196453','3','Season1_Tabs object (3)',1,'[{\"added\": {}}]',27,1),(155,'2022-09-08 10:31:40.029188','4','Season1_Tabs object (4)',1,'[{\"added\": {}}]',27,1),(156,'2022-09-08 10:38:26.817523','1','Season1_Bottom object (1)',1,'[{\"added\": {}}]',28,1),(157,'2022-09-09 10:53:44.985317','3','AboutTrials_Tabs object (3)',1,'[{\"added\": {}}]',23,1),(158,'2022-09-09 10:58:19.475670','22','MasterLabels object (22)',1,'[{\"added\": {}}]',9,1),(159,'2022-09-09 11:01:03.732313','23','MasterLabels object (23)',1,'[{\"added\": {}}]',9,1),(160,'2022-09-09 11:02:20.262273','24','MasterLabels object (24)',1,'[{\"added\": {}}]',9,1),(161,'2022-09-09 11:03:03.629065','22','MasterLabels object (22)',2,'[{\"changed\": {\"fields\": [\"Label\"]}}]',9,1),(162,'2022-09-09 11:24:23.160533','4','HomeBanner object (4)',2,'[{\"changed\": {\"fields\": [\"Heading 1\", \"Heading 2 colored\"]}}]',11,1),(163,'2022-09-09 11:26:18.100042','2','HomeBanner object (2)',2,'[{\"changed\": {\"fields\": [\"Heading 1\", \"Heading 2 colored\"]}}]',11,1),(164,'2022-09-09 11:26:44.473758','2','HomeBanner object (2)',2,'[{\"changed\": {\"fields\": [\"Heading 1\", \"Heading 2 colored\"]}}]',11,1),(165,'2022-09-09 11:37:13.548772','3','Winners object (3)',2,'[]',13,1),(166,'2022-09-09 11:37:16.441489','3','Winners object (3)',2,'[]',13,1),(167,'2022-09-09 11:37:40.748257','3','Winners object (3)',2,'[{\"changed\": {\"fields\": [\"Pic\"]}}]',13,1),(168,'2022-09-09 11:37:51.049985','2','Winners object (2)',2,'[{\"changed\": {\"fields\": [\"Pic\"]}}]',13,1),(169,'2022-09-09 11:38:02.189211','4','Winners object (4)',2,'[{\"changed\": {\"fields\": [\"Pic\"]}}]',13,1),(170,'2022-09-09 11:38:12.302160','5','Winners object (5)',2,'[{\"changed\": {\"fields\": [\"Pic\"]}}]',13,1),(171,'2022-09-09 11:39:17.202957','1','Partners object (1)',2,'[]',14,1),(172,'2022-09-09 11:39:24.277421','2','Partners object (2)',2,'[{\"changed\": {\"fields\": [\"Description\"]}}]',14,1),(173,'2022-09-09 11:39:31.250931','3','Partners object (3)',2,'[{\"changed\": {\"fields\": [\"Description\"]}}]',14,1),(174,'2022-09-09 11:39:41.469678','4','Partners object (4)',2,'[{\"changed\": {\"fields\": [\"Description\"]}}]',14,1),(175,'2022-09-09 11:55:36.099902','2','Winners object (2)',2,'[{\"changed\": {\"fields\": [\"Pic\"]}}]',13,1),(176,'2022-09-09 12:23:22.374553','6','Winners object (6)',1,'[{\"added\": {}}]',13,1),(177,'2022-09-09 12:27:43.955372','6','Winners object (6)',3,'',13,1);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(5,'contenttypes','contenttype'),(22,'main','abouttrials_bannerphoto'),(24,'main','abouttrials_bottom'),(25,'main','abouttrials_feature'),(23,'main','abouttrials_tabs'),(12,'main','aboutus'),(16,'main','buttons_ikf_for_all'),(11,'main','homebanner'),(10,'main','homeimages'),(15,'main','initiatives'),(7,'main','lang'),(9,'main','masterlabels'),(8,'main','navbar'),(18,'main','news'),(14,'main','partners'),(17,'main','photos_ikf_for_all'),(28,'main','season1_bottom'),(26,'main','season1_feature'),(27,'main','season1_tabs'),(20,'main','subtab'),(19,'main','tab'),(21,'main','test'),(13,'main','winners'),(6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2022-08-29 06:30:58.236406'),(2,'auth','0001_initial','2022-08-29 06:30:58.731899'),(3,'admin','0001_initial','2022-08-29 06:30:58.853787'),(4,'admin','0002_logentry_remove_auto_add','2022-08-29 06:30:58.877650'),(5,'admin','0003_logentry_add_action_flag_choices','2022-08-29 06:30:58.897547'),(6,'contenttypes','0002_remove_content_type_name','2022-08-29 06:30:58.979378'),(7,'auth','0002_alter_permission_name_max_length','2022-08-29 06:30:59.033353'),(8,'auth','0003_alter_user_email_max_length','2022-08-29 06:30:59.083042'),(9,'auth','0004_alter_user_username_opts','2022-08-29 06:30:59.108985'),(10,'auth','0005_alter_user_last_login_null','2022-08-29 06:30:59.153343'),(11,'auth','0006_require_contenttypes_0002','2022-08-29 06:30:59.157151'),(12,'auth','0007_alter_validators_add_error_messages','2022-08-29 06:30:59.180699'),(13,'auth','0008_alter_user_username_max_length','2022-08-29 06:30:59.202558'),(14,'auth','0009_alter_user_last_name_max_length','2022-08-29 06:30:59.224906'),(15,'auth','0010_alter_group_name_max_length','2022-08-29 06:30:59.263957'),(16,'auth','0011_update_proxy_permissions','2022-08-29 06:30:59.287773'),(17,'auth','0012_alter_user_first_name_max_length','2022-08-29 06:30:59.313357'),(18,'main','0001_initial','2022-08-29 06:30:59.691927'),(19,'main','0002_rename_heading_homebanner_heading_1_and_more','2022-08-29 06:30:59.817693'),(20,'main','0003_alter_homebanner_pic','2022-08-29 06:30:59.840812'),(21,'sessions','0001_initial','2022-08-29 06:30:59.878924'),(22,'main','0004_aboutus','2022-08-29 12:13:28.426829'),(23,'main','0005_rename_pic_aboutus_pic_1_aboutus_pic_2_aboutus_pic_3_and_more','2022-08-30 03:54:00.570756'),(24,'main','0006_remove_aboutus_button_text_remove_aboutus_heading_and_more','2022-08-30 05:17:09.566413'),(25,'main','0007_alter_winners_pic_1_alter_winners_pic_2_and_more','2022-08-30 05:44:34.232569'),(26,'main','0008_alter_winners_pic_1_alter_winners_pic_2_and_more','2022-08-30 05:48:17.656246'),(27,'main','0009_rename_category_1_winners_category_and_more','2022-08-30 07:17:11.493689'),(28,'main','0010_partners','2022-08-30 07:37:54.591352'),(29,'main','0011_initiatives','2022-08-30 08:18:36.657201'),(30,'main','0012_rename_button_initiatives_button_text','2022-08-30 08:22:50.446983'),(31,'main','0013_alter_initiatives_pic','2022-08-30 08:25:46.611811'),(32,'main','0014_initiatives_size','2022-08-30 08:29:18.650583'),(33,'main','0015_buttons_ikf_for_all','2022-08-30 09:00:28.459674'),(34,'main','0016_photos_ikf_for_all','2022-08-30 09:16:07.361474'),(35,'main','0017_alter_photos_ikf_for_all_pic','2022-08-30 09:27:32.677184'),(36,'main','0018_news','2022-08-30 10:52:34.053039'),(37,'main','0019_alter_news_date_alter_news_year','2022-08-30 10:52:34.104516'),(38,'main','0020_news_button_text','2022-08-30 11:11:37.122297'),(39,'main','0021_tab_subtab','2022-08-30 12:24:44.320145'),(40,'main','0022_test','2022-08-31 08:46:04.497886'),(41,'main','0023_abouttrials_bannerphoto_delete_test','2022-09-01 07:13:02.835566'),(42,'main','0024_alter_abouttrials_bannerphoto_pic','2022-09-01 07:41:29.493990'),(43,'main','0025_abouttrials_tabs','2022-09-01 08:25:13.829215'),(44,'main','0026_remove_abouttrials_tabs_size_abouttrials_bottom','2022-09-01 09:29:23.526383'),(45,'main','0027_abouttrials_feature','2022-09-01 10:09:09.941177'),(46,'main','0028_test','2022-09-01 16:19:12.157499'),(47,'main','0029_season1_feature_delete_test','2022-09-08 10:17:15.139777'),(48,'main','0030_season1_tabs','2022-09-08 10:25:52.874263'),(49,'main','0031_season1_bottom','2022-09-08 10:37:23.166347'),(50,'main','0032_abouttrials_tabs_button_text_and_more','2022-09-09 10:47:49.913317'),(51,'main','0033_remove_abouttrials_tabs_button_text_and_more','2022-09-09 10:56:23.683453'),(52,'main','0034_initiatives_initiative_href','2022-09-09 11:44:38.838791');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('i8e0s83wkexlpk3kl26vn6mu8dcbdqkp','.eJxVjMsOwiAQRf-FtSEMryEu3fsNBBhGqoYmpV0Z_12bdKHbe865LxHTtra4jbrEicRZgDj9bjmVR-07oHvqt1mWua_LlOWuyIMOeZ2pPi-H-3fQ0mjf2jAq733VqHJQ2WBVLhuHDslCUonYGrS6gi4cGIIjMpZQMyAUx0G8P8IiN0E:1oSYbP:8l3H53Bsi3CdMCZhdZFuRdedZZbb5inQ_Nqguz0XgKw','2022-09-12 06:50:31.861773'),('wmyrj2bj1swsi0v0531d8iwi67f6ltro','.eJxVjMsOwiAQRf-FtSEMryEu3fsNBBhGqoYmpV0Z_12bdKHbe865LxHTtra4jbrEicRZgDj9bjmVR-07oHvqt1mWua_LlOWuyIMOeZ2pPi-H-3fQ0mjf2jAq733VqHJQ2WBVLhuHDslCUonYGrS6gi4cGIIjMpZQMyAUx0G8P8IiN0E:1oSYKP:kOPNZaAx4rPMFE-3hwJTil5rQbPaFV8knzDm1b-4gJk','2022-09-12 06:32:57.399432');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `main_abouttrials_bannerphoto`
--

DROP TABLE IF EXISTS `main_abouttrials_bannerphoto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `main_abouttrials_bannerphoto` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `keydata` varchar(200) DEFAULT NULL,
  `size` varchar(100) DEFAULT NULL,
  `pic` varchar(100) DEFAULT NULL,
  `lang_id` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `main_abouttrials_bannerphoto_lang_id_ac65e760_fk_main_lang_id` (`lang_id`),
  KEY `main_abouttrials_bannerphoto_keydata_97395cfe` (`keydata`),
  CONSTRAINT `main_abouttrials_bannerphoto_lang_id_ac65e760_fk_main_lang_id` FOREIGN KEY (`lang_id`) REFERENCES `main_lang` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `main_abouttrials_bannerphoto`
--

LOCK TABLES `main_abouttrials_bannerphoto` WRITE;
/*!40000 ALTER TABLE `main_abouttrials_bannerphoto` DISABLE KEYS */;
INSERT INTO `main_abouttrials_bannerphoto` VALUES (3,'test',NULL,'media/ui/bannerphoto/736150.jpg','en');
/*!40000 ALTER TABLE `main_abouttrials_bannerphoto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `main_abouttrials_feature`
--

DROP TABLE IF EXISTS `main_abouttrials_feature`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `main_abouttrials_feature` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `keydata` varchar(200) DEFAULT NULL,
  `size` varchar(100) DEFAULT NULL,
  `pic` varchar(100) DEFAULT NULL,
  `name` varchar(200) DEFAULT NULL,
  `description` varchar(1000) DEFAULT NULL,
  `attr1` varchar(200) DEFAULT NULL,
  `attr2` varchar(200) DEFAULT NULL,
  `attr3` varchar(200) DEFAULT NULL,
  `attr4` varchar(200) DEFAULT NULL,
  `lang_id` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `main_abouttrials_feature_lang_id_95c796ed_fk_main_lang_id` (`lang_id`),
  KEY `main_abouttrials_feature_keydata_b8773c8d` (`keydata`),
  CONSTRAINT `main_abouttrials_feature_lang_id_95c796ed_fk_main_lang_id` FOREIGN KEY (`lang_id`) REFERENCES `main_lang` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `main_abouttrials_feature`
--

LOCK TABLES `main_abouttrials_feature` WRITE;
/*!40000 ALTER TABLE `main_abouttrials_feature` DISABLE KEYS */;
INSERT INTO `main_abouttrials_feature` VALUES (1,'sample',NULL,'media/ui/Features/2.jpg','asdasd','asdasdasd',NULL,NULL,NULL,NULL,'en'),(2,'test','483x430','media/ui/Features/736150.jpg','Play Abroad','Reliance Industries Limited is an Indian multinational conglomerate company, headquartered in Mumbai. It has diverse businesses including energy, petrochemicals, natural gas, retail, telecommunication',NULL,NULL,NULL,NULL,'en');
/*!40000 ALTER TABLE `main_abouttrials_feature` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `main_abouttrials_tabs`
--

DROP TABLE IF EXISTS `main_abouttrials_tabs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `main_abouttrials_tabs` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `keydata` varchar(200) DEFAULT NULL,
  `name` varchar(1000) DEFAULT NULL,
  `attr1` varchar(200) DEFAULT NULL,
  `attr2` varchar(200) DEFAULT NULL,
  `attr3` varchar(200) DEFAULT NULL,
  `attr4` varchar(200) DEFAULT NULL,
  `lang_id` varchar(100) DEFAULT NULL,
  `href` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `main_abouttrials_tabs_lang_id_6e853d06_fk_main_lang_id` (`lang_id`),
  KEY `main_abouttrials_tabs_keydata_fbd42340` (`keydata`),
  CONSTRAINT `main_abouttrials_tabs_lang_id_6e853d06_fk_main_lang_id` FOREIGN KEY (`lang_id`) REFERENCES `main_lang` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `main_abouttrials_tabs`
--

LOCK TABLES `main_abouttrials_tabs` WRITE;
/*!40000 ALTER TABLE `main_abouttrials_tabs` DISABLE KEYS */;
INSERT INTO `main_abouttrials_tabs` VALUES (1,'sample','Season 1 [2021-22]',NULL,NULL,NULL,NULL,'en',NULL),(2,'sample','Season 2 [2022-23]',NULL,NULL,NULL,NULL,'en',NULL),(3,'tabs','Season 1 [2021-22]',NULL,NULL,NULL,NULL,'en','Season 1 [2021-22]');
/*!40000 ALTER TABLE `main_abouttrials_tabs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `main_aboutus`
--

DROP TABLE IF EXISTS `main_aboutus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `main_aboutus` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `keydata` varchar(200) DEFAULT NULL,
  `size` varchar(100) DEFAULT NULL,
  `pic_1` varchar(100) DEFAULT NULL,
  `attr1` varchar(200) DEFAULT NULL,
  `attr2` varchar(200) DEFAULT NULL,
  `attr3` varchar(200) DEFAULT NULL,
  `attr4` varchar(200) DEFAULT NULL,
  `lang_id` varchar(100) DEFAULT NULL,
  `pic_2` varchar(100) DEFAULT NULL,
  `pic_3` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `main_aboutus_lang_id_80736292_fk_main_lang_id` (`lang_id`),
  KEY `main_aboutus_keydata_1c28f1b1` (`keydata`),
  CONSTRAINT `main_aboutus_lang_id_80736292_fk_main_lang_id` FOREIGN KEY (`lang_id`) REFERENCES `main_lang` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `main_aboutus`
--

LOCK TABLES `main_aboutus` WRITE;
/*!40000 ALTER TABLE `main_aboutus` DISABLE KEYS */;
INSERT INTO `main_aboutus` VALUES (1,'about us','155x254','media/ui/aboutus/images.jpeg',NULL,NULL,NULL,NULL,'en','media/ui/aboutus/2_1.jpeg','media/ui/aboutus/3_1.jpeg');
/*!40000 ALTER TABLE `main_aboutus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `main_buttons_ikf_for_all`
--

DROP TABLE IF EXISTS `main_buttons_ikf_for_all`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `main_buttons_ikf_for_all` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `keydata` varchar(200) DEFAULT NULL,
  `button_text` varchar(100) DEFAULT NULL,
  `attr1` varchar(200) DEFAULT NULL,
  `attr2` varchar(200) DEFAULT NULL,
  `attr3` varchar(200) DEFAULT NULL,
  `attr4` varchar(200) DEFAULT NULL,
  `lang_id` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `main_buttons_ikf_for_all_lang_id_acddbeb4_fk_main_lang_id` (`lang_id`),
  KEY `main_buttons_ikf_for_all_keydata_c0ca6acf` (`keydata`),
  CONSTRAINT `main_buttons_ikf_for_all_lang_id_acddbeb4_fk_main_lang_id` FOREIGN KEY (`lang_id`) REFERENCES `main_lang` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `main_buttons_ikf_for_all`
--

LOCK TABLES `main_buttons_ikf_for_all` WRITE;
/*!40000 ALTER TABLE `main_buttons_ikf_for_all` DISABLE KEYS */;
INSERT INTO `main_buttons_ikf_for_all` VALUES (1,'buttons','All',NULL,NULL,NULL,NULL,'en'),(2,'buttons','Players',NULL,NULL,NULL,NULL,'en'),(3,'buttons','Parents',NULL,NULL,NULL,NULL,'en'),(4,'buttons','Coach',NULL,NULL,NULL,NULL,'en'),(5,'buttons','Academy',NULL,NULL,NULL,NULL,'en'),(6,'buttons','Club',NULL,NULL,NULL,NULL,'en'),(7,'buttons','Aspiring Scout',NULL,NULL,NULL,NULL,'en');
/*!40000 ALTER TABLE `main_buttons_ikf_for_all` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `main_homebanner`
--

DROP TABLE IF EXISTS `main_homebanner`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `main_homebanner` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `keydata` varchar(200) DEFAULT NULL,
  `size` varchar(100) DEFAULT NULL,
  `pic` varchar(100) DEFAULT NULL,
  `name` varchar(200) DEFAULT NULL,
  `heading_1` varchar(200) DEFAULT NULL,
  `description` longtext DEFAULT NULL,
  `attr1` varchar(200) DEFAULT NULL,
  `attr2` varchar(200) DEFAULT NULL,
  `attr3` varchar(200) DEFAULT NULL,
  `attr4` varchar(200) DEFAULT NULL,
  `lang_id` varchar(100) DEFAULT NULL,
  `button1_text` varchar(100) DEFAULT NULL,
  `button2_text` varchar(100) DEFAULT NULL,
  `heading_2_colored` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `main_homebanner_lang_id_cf8e616d_fk_main_lang_id` (`lang_id`),
  KEY `main_homebanner_keydata_4bd20fb3` (`keydata`),
  CONSTRAINT `main_homebanner_lang_id_cf8e616d_fk_main_lang_id` FOREIGN KEY (`lang_id`) REFERENCES `main_lang` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `main_homebanner`
--

LOCK TABLES `main_homebanner` WRITE;
/*!40000 ALTER TABLE `main_homebanner` DISABLE KEYS */;
INSERT INTO `main_homebanner` VALUES (1,'1st banner','1920x766','media/ui/homebanner/17141465.jpg','IKF Season 2','Biggest Trials in','India Khelo Football is back with Season 2 – Biggest Trials in India. A 24+ city talent hunt converging in Mega Finals where scouts from all top most Indian Clubs & International academies will be present. 7 Kids will win Free Trials in Europe.','first banner',NULL,NULL,NULL,'en','Read More','ContactUs','India'),(2,'2nd banner','1920x766','media/ui/homebanner/17141420.jpg','Become IKF Partner Scout','Certification','India Khelo Football has partnered with PFSA, UK to develop scouting ecosystem from scratch in India. Launching certification program under mentorship of ProSoccerGlobal. Become an IKF scout & start earning!','Second banner',NULL,NULL,NULL,'en','Read More','ContactUs','program'),(3,'3rd banner','1920x766','media/ui/homebanner/10779720.jpg','Workshops powered by IKF','Premier League scouts & agents in','ProSoccerGlobal is coming to India and bringing with them 100% scholarship to Steven Gerrard academy, UK. Get assessed & feedback from Premier League scouts & agent here in India.','third banner',NULL,NULL,NULL,'en','Read More','ContactUs','India !'),(4,'4rth banner','1920x766','media/ui/homebanner/736150.jpg','Play Abroad','Counselling','Advance your career abroad by getting right advice from IKF. Counselling for aspiring & established football players who are seeking opportunities abroad.','fourth banner',NULL,NULL,NULL,'en','Read More','ContactUs','Program');
/*!40000 ALTER TABLE `main_homebanner` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `main_homeimages`
--

DROP TABLE IF EXISTS `main_homeimages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `main_homeimages` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `keydata` varchar(200) DEFAULT NULL,
  `name` varchar(200) DEFAULT NULL,
  `size` varchar(100) DEFAULT NULL,
  `pic` varchar(100) DEFAULT NULL,
  `attr1` varchar(200) DEFAULT NULL,
  `attr2` varchar(200) DEFAULT NULL,
  `attr3` varchar(200) DEFAULT NULL,
  `attr4` varchar(200) DEFAULT NULL,
  `lang_id` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `main_homeimages_lang_id_3a3017b3_fk_main_lang_id` (`lang_id`),
  KEY `main_homeimages_keydata_cd7697ed` (`keydata`),
  CONSTRAINT `main_homeimages_lang_id_3a3017b3_fk_main_lang_id` FOREIGN KEY (`lang_id`) REFERENCES `main_lang` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `main_homeimages`
--

LOCK TABLES `main_homeimages` WRITE;
/*!40000 ALTER TABLE `main_homeimages` DISABLE KEYS */;
/*!40000 ALTER TABLE `main_homeimages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `main_initiatives`
--

DROP TABLE IF EXISTS `main_initiatives`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `main_initiatives` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `keydata` varchar(200) DEFAULT NULL,
  `name` varchar(200) DEFAULT NULL,
  `pic` varchar(100) DEFAULT NULL,
  `description` varchar(1000) DEFAULT NULL,
  `button_text` varchar(100) DEFAULT NULL,
  `attr1` varchar(200) DEFAULT NULL,
  `attr2` varchar(200) DEFAULT NULL,
  `attr3` varchar(200) DEFAULT NULL,
  `attr4` varchar(200) DEFAULT NULL,
  `lang_id` varchar(100) DEFAULT NULL,
  `size` varchar(100) DEFAULT NULL,
  `initiative_href` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `main_initiatives_lang_id_3ad76c38_fk_main_lang_id` (`lang_id`),
  KEY `main_initiatives_keydata_798574d5` (`keydata`),
  CONSTRAINT `main_initiatives_lang_id_3ad76c38_fk_main_lang_id` FOREIGN KEY (`lang_id`) REFERENCES `main_lang` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `main_initiatives`
--

LOCK TABLES `main_initiatives` WRITE;
/*!40000 ALTER TABLE `main_initiatives` DISABLE KEYS */;
INSERT INTO `main_initiatives` VALUES (1,'IKF’s Trials','IKF’s Trials','media/ui/partners/images_2.jpeg','India Khelo Football conducts Pan India Trials every season, scouts exceptional talent and connects them with top most opportunities.','Read More',NULL,NULL,NULL,NULL,'en','292x292',NULL),(2,'initiatives','Scouting Certification','media/ui/initiatives/players2.jpeg','International certification program in India to create scouts. Become IKF Partner Scout & start earning.','Read More',NULL,NULL,NULL,NULL,'en','292x292',NULL),(3,'IKF_Initiative_home','Play Abroad','media/ui/initiatives/2.png','Counselling program by IKF for players who wish to advance their career outside India. Scientific approach and genuine options.','Read More',NULL,NULL,NULL,NULL,'en','292x292',NULL),(4,'IKF_Initiative_home','Workshop by Premier League Scouts','media/ui/initiatives/3_1.jpeg','Premier league scouts & agents in India for aspiring football players. Get assessed & win 100% scholarship in UK.','Read More',NULL,NULL,NULL,NULL,'en','292x292',NULL);
/*!40000 ALTER TABLE `main_initiatives` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `main_lang`
--

DROP TABLE IF EXISTS `main_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `main_lang` (
  `id` varchar(100) NOT NULL,
  `lang` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `main_lang`
--

LOCK TABLES `main_lang` WRITE;
/*!40000 ALTER TABLE `main_lang` DISABLE KEYS */;
INSERT INTO `main_lang` VALUES ('en','en'),('eng','english');
/*!40000 ALTER TABLE `main_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `main_masterlabels`
--

DROP TABLE IF EXISTS `main_masterlabels`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `main_masterlabels` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `keydata` varchar(200) DEFAULT NULL,
  `label` longtext DEFAULT NULL,
  `extrainfo` varchar(200) DEFAULT NULL,
  `lang_id` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `main_masterlabels_lang_id_fa18fb92_fk_main_lang_id` (`lang_id`),
  KEY `main_masterlabels_keydata_650f839e` (`keydata`),
  CONSTRAINT `main_masterlabels_lang_id_fa18fb92_fk_main_lang_id` FOREIGN KEY (`lang_id`) REFERENCES `main_lang` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `main_masterlabels`
--

LOCK TABLES `main_masterlabels` WRITE;
/*!40000 ALTER TABLE `main_masterlabels` DISABLE KEYS */;
INSERT INTO `main_masterlabels` VALUES (1,'about_us_name','About Us','home','en'),(2,'about_us_paragraph_1','India Khelo Football is a not-for-profit initiative strengthening grassroots ecosystem in India. It is platform which connects aspiring football players with opportunities. It is platform created to establish a steady talent pipeline for Indian Football.','about_us_paragraph_1','en'),(3,'about_us_heading','Mission','about_us_heading','en'),(4,'about_us_paragraph_2','Create a structured career path for aspiring football players in India. All our activities revolve around this. This would help us achieve the following\r\nMake India feeder of talent to world\r\nCreate 100K+ professional football players\r\nIndia qualifies for 2034 world cup','about_us_paragraph_2','en'),(5,'about_us_button','Read More','about_us_button','en'),(6,'trials_home','IKF\'s  Upcoming  Season2 Trials','trials_home','en'),(7,'winners_home','Winners of Season 1','winners_home','en'),(8,'winners_paragraph','We conducted Trials in 17 cities across India and assessed 3000+ kids. 104 exceptional talent scouted from these 17 cities qualified for National Finals where these 7 kids won Free Trials in Spain.','winners_paragraph','en'),(9,'IKF_Initiative_home','IKF’s Crown Initiatives','IKF’s Crown Initiatives','en'),(10,'services_home','IKF for All','IKF for All','en'),(11,'news_home','IKF In News !!','IKF In News !!','en'),(12,'Heading_IKF_Trials','Heading','Heading','en'),(13,'Paragraph_IKF_Trials','In 1977, Reliance Textile Industries’ IPO creates history by introducing the equity cult in India. The issue is oversubscribed seven times, strengthening Reliance’s growth ambitions.','Paragraph_IKF_Trials','en'),(14,'description_IKF_Trials','In 2004, Reliance emerges as the first and only private Indian organisation to be listed in the Fortune Global 500 list. Reliance is also the first private sector company to be rated by international credit rating agencies - including Moody\'s, Standard and Poor\'s.','description_IKF_Trials','en'),(16,'button_IKF_Trials','Read More','Read More','en'),(17,'Heading_season1','test','Heading','en'),(18,'Heading_season1','Season1','Heading','en'),(19,'Paragraph_season1','this is paragraph','Paragraph_IKF_Trials','en'),(20,'description_season1','this is description','description','en'),(21,'button_season1','Read More','Read More','en'),(22,'ikftrials_description','Paragraphs are the building blocks of papers. Many students define paragraphs in terms of length: a paragraph is a group of at least five sentences, a paragraph is half a page long, etc. In reality, though, the unity and coherence of ideas among sentences is what constitutes a paragraph. A paragraph is defined as “a group of sentences or a single sentence that forms a unit” (Lunsford and Connors 116). Length and appearance do not determine whether a section in a paper is a paragraph. For instance, in some styles of writing, particularly journalistic styles, a paragraph can be just one sentence long. Ultimately, a paragraph is a sentence or group of sentences that support one main idea. In this handout, we will refer to this as the “controlling idea,” because it controls what happens in the rest of the paragraph.','this is test description','en'),(23,'ikftrials_href_bottom','season1.html','season1.html','en'),(24,'ikftrials_button_text','Read More','Read More Button','en');
/*!40000 ALTER TABLE `main_masterlabels` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `main_navbar`
--

DROP TABLE IF EXISTS `main_navbar`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `main_navbar` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `keydata` varchar(200) DEFAULT NULL,
  `name` varchar(200) DEFAULT NULL,
  `urlitem` varchar(200) DEFAULT NULL,
  `attr1` varchar(200) DEFAULT NULL,
  `attr2` varchar(200) DEFAULT NULL,
  `attr3` varchar(200) DEFAULT NULL,
  `attr4` varchar(200) DEFAULT NULL,
  `lang_id` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `main_navbar_lang_id_e3a91f6f_fk_main_lang_id` (`lang_id`),
  KEY `main_navbar_keydata_48fc8d19` (`keydata`),
  CONSTRAINT `main_navbar_lang_id_e3a91f6f_fk_main_lang_id` FOREIGN KEY (`lang_id`) REFERENCES `main_lang` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `main_navbar`
--

LOCK TABLES `main_navbar` WRITE;
/*!40000 ALTER TABLE `main_navbar` DISABLE KEYS */;
/*!40000 ALTER TABLE `main_navbar` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `main_news`
--

DROP TABLE IF EXISTS `main_news`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `main_news` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `keydata` varchar(200) DEFAULT NULL,
  `size` varchar(100) DEFAULT NULL,
  `pic` varchar(100) DEFAULT NULL,
  `name` varchar(200) DEFAULT NULL,
  `heading` varchar(200) DEFAULT NULL,
  `description` varchar(1000) DEFAULT NULL,
  `date` int(11) DEFAULT NULL,
  `year` int(11) DEFAULT NULL,
  `attr1` varchar(200) DEFAULT NULL,
  `attr2` varchar(200) DEFAULT NULL,
  `attr3` varchar(200) DEFAULT NULL,
  `attr4` varchar(200) DEFAULT NULL,
  `lang_id` varchar(100) DEFAULT NULL,
  `button_text` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `main_news_lang_id_6455fa55_fk_main_lang_id` (`lang_id`),
  KEY `main_news_keydata_fa0755ed` (`keydata`),
  CONSTRAINT `main_news_lang_id_6455fa55_fk_main_lang_id` FOREIGN KEY (`lang_id`) REFERENCES `main_lang` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `main_news`
--

LOCK TABLES `main_news` WRITE;
/*!40000 ALTER TABLE `main_news` DISABLE KEYS */;
INSERT INTO `main_news` VALUES (1,'news','855x897','media/ui/news/images_2.jpeg','shubham thakur','aaj tak','ikf news',25,2020,NULL,NULL,NULL,NULL,'en',NULL),(2,'news','637x631','media/ui/news/3_1.jpeg','antony','patrika','ikf in news',45,22,NULL,NULL,NULL,NULL,'en',NULL);
/*!40000 ALTER TABLE `main_news` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `main_partners`
--

DROP TABLE IF EXISTS `main_partners`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `main_partners` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `keydata` varchar(200) DEFAULT NULL,
  `name` varchar(200) DEFAULT NULL,
  `pic` varchar(100) DEFAULT NULL,
  `description` varchar(200) DEFAULT NULL,
  `attr1` varchar(200) DEFAULT NULL,
  `attr2` varchar(200) DEFAULT NULL,
  `attr3` varchar(200) DEFAULT NULL,
  `attr4` varchar(200) DEFAULT NULL,
  `lang_id` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `main_partners_lang_id_6e008298_fk_main_lang_id` (`lang_id`),
  KEY `main_partners_keydata_48cd644d` (`keydata`),
  CONSTRAINT `main_partners_lang_id_6e008298_fk_main_lang_id` FOREIGN KEY (`lang_id`) REFERENCES `main_lang` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `main_partners`
--

LOCK TABLES `main_partners` WRITE;
/*!40000 ALTER TABLE `main_partners` DISABLE KEYS */;
INSERT INTO `main_partners` VALUES (1,'partners','reliance','media/ui/partners/1.png','Reliance Industries Limited is an Indian multinational conglomerate company, headquartered in Mumbai. It has diverse businesses including energy, petrochemicals, natural gas, retail, telecommunication',NULL,NULL,NULL,NULL,'en'),(2,'partners','tata','media/ui/partners/tata.jpeg','Reliance Industries Limited is an Indian multinational conglomerate company, headquartered in Mumbai. It has diverse businesses including energy, petrochemicals, natural gas, retail, telecommunication',NULL,NULL,NULL,NULL,'en'),(3,'partners','Trident','media/ui/partners/2.png','Reliance Industries Limited is an Indian multinational conglomerate company, headquartered in Mumbai. It has diverse businesses including energy, petrochemicals, natural gas, retail, telecommunication',NULL,NULL,NULL,NULL,'en'),(4,'partners','Adani','media/ui/partners/4.jpeg','Reliance Industries Limited is an Indian multinational conglomerate company, headquartered in Mumbai. It has diverse businesses including energy, petrochemicals, natural gas, retail, telecommunication',NULL,NULL,NULL,NULL,'en');
/*!40000 ALTER TABLE `main_partners` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `main_photos_ikf_for_all`
--

DROP TABLE IF EXISTS `main_photos_ikf_for_all`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `main_photos_ikf_for_all` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `keydata` varchar(200) DEFAULT NULL,
  `size` varchar(100) DEFAULT NULL,
  `pic` varchar(100) DEFAULT NULL,
  `attr1` varchar(200) DEFAULT NULL,
  `attr2` varchar(200) DEFAULT NULL,
  `attr3` varchar(200) DEFAULT NULL,
  `attr4` varchar(200) DEFAULT NULL,
  `lang_id` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `main_photos_ikf_for_all_lang_id_3a8a5207_fk_main_lang_id` (`lang_id`),
  KEY `main_photos_ikf_for_all_keydata_7d7a33cb` (`keydata`),
  CONSTRAINT `main_photos_ikf_for_all_lang_id_3a8a5207_fk_main_lang_id` FOREIGN KEY (`lang_id`) REFERENCES `main_lang` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `main_photos_ikf_for_all`
--

LOCK TABLES `main_photos_ikf_for_all` WRITE;
/*!40000 ALTER TABLE `main_photos_ikf_for_all` DISABLE KEYS */;
INSERT INTO `main_photos_ikf_for_all` VALUES (2,'phots','483x430','media/ui/photos/2.png',NULL,NULL,NULL,NULL,'en'),(3,'photos','483x430','media/ui/photos/17141420.jpg',NULL,NULL,NULL,NULL,'en'),(4,'photos','483x430','media/ui/photos/3_1.jpeg',NULL,NULL,NULL,NULL,'en'),(5,'photos','483x430','media/ui/photos/images.jpeg',NULL,NULL,NULL,NULL,'en'),(6,'photos','483x430','media/ui/photos/Cool-4K-Football-Wallpaper-HD.jpg',NULL,NULL,NULL,NULL,'en'),(7,'photos','483x430','media/ui/photos/10779720.jpg',NULL,NULL,NULL,NULL,'en'),(8,'photos','483x430','media/ui/photos/17141420.jpg',NULL,NULL,NULL,NULL,'en'),(9,'photos','483x430','media/ui/photos/background1.webp',NULL,NULL,NULL,NULL,'en');
/*!40000 ALTER TABLE `main_photos_ikf_for_all` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `main_season1_bottom`
--

DROP TABLE IF EXISTS `main_season1_bottom`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `main_season1_bottom` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `keydata` varchar(200) DEFAULT NULL,
  `description` varchar(1000) DEFAULT NULL,
  `button_text` varchar(100) DEFAULT NULL,
  `attr1` varchar(200) DEFAULT NULL,
  `attr2` varchar(200) DEFAULT NULL,
  `attr3` varchar(200) DEFAULT NULL,
  `attr4` varchar(200) DEFAULT NULL,
  `lang_id` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `main_season1_bottom_lang_id_5b47fd37_fk_main_lang_id` (`lang_id`),
  KEY `main_season1_bottom_keydata_91f4dc3a` (`keydata`),
  CONSTRAINT `main_season1_bottom_lang_id_5b47fd37_fk_main_lang_id` FOREIGN KEY (`lang_id`) REFERENCES `main_lang` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `main_season1_bottom`
--

LOCK TABLES `main_season1_bottom` WRITE;
/*!40000 ALTER TABLE `main_season1_bottom` DISABLE KEYS */;
INSERT INTO `main_season1_bottom` VALUES (1,'data','this is description','Read More',NULL,NULL,NULL,NULL,'en');
/*!40000 ALTER TABLE `main_season1_bottom` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `main_season1_feature`
--

DROP TABLE IF EXISTS `main_season1_feature`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `main_season1_feature` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `keydata` varchar(200) DEFAULT NULL,
  `size` varchar(100) DEFAULT NULL,
  `pic` varchar(100) DEFAULT NULL,
  `name` varchar(200) DEFAULT NULL,
  `description` varchar(1000) DEFAULT NULL,
  `attr1` varchar(200) DEFAULT NULL,
  `attr2` varchar(200) DEFAULT NULL,
  `attr3` varchar(200) DEFAULT NULL,
  `attr4` varchar(200) DEFAULT NULL,
  `lang_id` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `main_season1_feature_lang_id_6df4a0c3_fk_main_lang_id` (`lang_id`),
  KEY `main_season1_feature_keydata_0c16b8a5` (`keydata`),
  CONSTRAINT `main_season1_feature_lang_id_6df4a0c3_fk_main_lang_id` FOREIGN KEY (`lang_id`) REFERENCES `main_lang` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `main_season1_feature`
--

LOCK TABLES `main_season1_feature` WRITE;
/*!40000 ALTER TABLE `main_season1_feature` DISABLE KEYS */;
INSERT INTO `main_season1_feature` VALUES (1,'season1_feature',NULL,'media/ui/Season1/tata.jpeg','Season1','this is season 1 feature',NULL,NULL,NULL,NULL,'en');
/*!40000 ALTER TABLE `main_season1_feature` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `main_season1_tabs`
--

DROP TABLE IF EXISTS `main_season1_tabs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `main_season1_tabs` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `keydata` varchar(200) DEFAULT NULL,
  `name` varchar(1000) DEFAULT NULL,
  `attr1` varchar(200) DEFAULT NULL,
  `attr2` varchar(200) DEFAULT NULL,
  `attr3` varchar(200) DEFAULT NULL,
  `attr4` varchar(200) DEFAULT NULL,
  `lang_id` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `main_season1_tabs_lang_id_dbcb12ce_fk_main_lang_id` (`lang_id`),
  KEY `main_season1_tabs_keydata_89cad9ff` (`keydata`),
  CONSTRAINT `main_season1_tabs_lang_id_dbcb12ce_fk_main_lang_id` FOREIGN KEY (`lang_id`) REFERENCES `main_lang` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `main_season1_tabs`
--

LOCK TABLES `main_season1_tabs` WRITE;
/*!40000 ALTER TABLE `main_season1_tabs` DISABLE KEYS */;
INSERT INTO `main_season1_tabs` VALUES (1,'Description','Description',NULL,NULL,NULL,NULL,'en'),(2,'Cities covered','Cities covered',NULL,NULL,NULL,NULL,'en'),(3,'Clubs which participated','Clubs which participated',NULL,NULL,NULL,NULL,'en'),(4,'Selections','Selections',NULL,NULL,NULL,NULL,'en');
/*!40000 ALTER TABLE `main_season1_tabs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `main_subtab`
--

DROP TABLE IF EXISTS `main_subtab`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `main_subtab` (
  `id` varchar(100) NOT NULL,
  `subtab` varchar(200) DEFAULT NULL,
  `tab_id` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `main_subtab_tab_id_f34a8971_fk_main_tab_id` (`tab_id`),
  KEY `main_subtab_subtab_76369ff4` (`subtab`),
  CONSTRAINT `main_subtab_tab_id_f34a8971_fk_main_tab_id` FOREIGN KEY (`tab_id`) REFERENCES `main_tab` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `main_subtab`
--

LOCK TABLES `main_subtab` WRITE;
/*!40000 ALTER TABLE `main_subtab` DISABLE KEYS */;
/*!40000 ALTER TABLE `main_subtab` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `main_tab`
--

DROP TABLE IF EXISTS `main_tab`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `main_tab` (
  `id` varchar(100) NOT NULL,
  `tab` varchar(200) DEFAULT NULL,
  `extra` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `main_tab_tab_100e4618` (`tab`),
  KEY `main_tab_extra_5dc8f003` (`extra`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `main_tab`
--

LOCK TABLES `main_tab` WRITE;
/*!40000 ALTER TABLE `main_tab` DISABLE KEYS */;
INSERT INTO `main_tab` VALUES ('Home','Home','Home');
/*!40000 ALTER TABLE `main_tab` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `main_winners`
--

DROP TABLE IF EXISTS `main_winners`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `main_winners` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `keydata` varchar(200) DEFAULT NULL,
  `size` varchar(100) DEFAULT NULL,
  `pic` varchar(100) DEFAULT NULL,
  `category` varchar(200) DEFAULT NULL,
  `name` varchar(200) DEFAULT NULL,
  `attr1` varchar(200) DEFAULT NULL,
  `attr2` varchar(200) DEFAULT NULL,
  `attr3` varchar(200) DEFAULT NULL,
  `attr4` varchar(200) DEFAULT NULL,
  `lang_id` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `main_winners_lang_id_6b253b37_fk_main_lang_id` (`lang_id`),
  KEY `main_winners_keydata_a2fe4109` (`keydata`),
  CONSTRAINT `main_winners_lang_id_6b253b37_fk_main_lang_id` FOREIGN KEY (`lang_id`) REFERENCES `main_lang` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `main_winners`
--

LOCK TABLES `main_winners` WRITE;
/*!40000 ALTER TABLE `main_winners` DISABLE KEYS */;
INSERT INTO `main_winners` VALUES (2,'winners','500x600','media/ui/winners/images_1.jpeg','middle','ronaldo',NULL,NULL,NULL,NULL,'en'),(3,'winners','500x600','media/ui/winners/images_1.jpeg','middle','messi',NULL,NULL,NULL,NULL,'en'),(4,'winners','500x600','media/ui/winners/images_1.jpeg','forward','pepe',NULL,NULL,NULL,NULL,'en'),(5,'winners','500x600','media/ui/winners/images_1.jpeg','forward','neymar',NULL,NULL,NULL,NULL,'en');
/*!40000 ALTER TABLE `main_winners` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-09-09 17:59:53
