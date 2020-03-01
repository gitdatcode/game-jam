# ************************************************************
# Sequel Pro SQL dump
# Version 4541
#
# http://www.sequelpro.com/
# https://github.com/sequelpro/sequelpro
#
# Host: 127.0.0.1 (MySQL 5.5.5-10.3.22-MariaDB)
# Database: game_jam
# Generation Time: 2020-03-01 16:09:13 +0000
# ************************************************************


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


# Dump of table basemodel
# ------------------------------------------------------------

DROP TABLE IF EXISTS `basemodel`;

CREATE TABLE `basemodel` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table scene
# ------------------------------------------------------------

DROP TABLE IF EXISTS `scene`;

CREATE TABLE `scene` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `story_id` int(11) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `content` text NOT NULL,
  `order` int(11) NOT NULL,
  `image` text DEFAULT NULL,
  `image_mobile` text DEFAULT NULL,
  `sound_load` text DEFAULT NULL,
  `sound_unload` text DEFAULT NULL,
  `sound_background` text DEFAULT NULL,
  `css` text DEFAULT NULL,
  `js` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `scene_story_id` (`story_id`),
  CONSTRAINT `fk_scene_story_id_refs_story` FOREIGN KEY (`story_id`) REFERENCES `story` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

LOCK TABLES `scene` WRITE;
/*!40000 ALTER TABLE `scene` DISABLE KEYS */;

INSERT INTO `scene` (`id`, `story_id`, `title`, `content`, `order`, `image`, `image_mobile`, `sound_load`, `sound_unload`, `sound_background`, `css`, `js`)
VALUES
	(1,1,'first scene','this is the first scene. it has three options',0,'image1',NULL,'/static/audio/sound1',NULL,NULL,NULL,NULL),
	(2,1,'second scene','sescene',0,'image2	',NULL,'/static/audio/sound2',NULL,NULL,NULL,NULL);

/*!40000 ALTER TABLE `scene` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table sceneoption
# ------------------------------------------------------------

DROP TABLE IF EXISTS `sceneoption`;

CREATE TABLE `sceneoption` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `scene_id` int(11) NOT NULL,
  `order` int(11) NOT NULL,
  `text` text NOT NULL,
  `tool_tip` text DEFAULT NULL,
  `value` float NOT NULL,
  `next_scene` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `sceneoption_scene_id` (`scene_id`),
  CONSTRAINT `fk_sceneoption_scene_id_refs_scene` FOREIGN KEY (`scene_id`) REFERENCES `scene` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

LOCK TABLES `sceneoption` WRITE;
/*!40000 ALTER TABLE `sceneoption` DISABLE KEYS */;

INSERT INTO `sceneoption` (`id`, `scene_id`, `order`, `text`, `tool_tip`, `value`, `next_scene`)
VALUES
	(1,1,0,'option one',NULL,1,2),
	(2,2,0,'option two',NULL,2,0),
	(3,1,2,'option two',NULL,4,0),
	(4,1,1,'three	',NULL,4,0);

/*!40000 ALTER TABLE `sceneoption` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table story
# ------------------------------------------------------------

DROP TABLE IF EXISTS `story`;

CREATE TABLE `story` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `image` text DEFAULT NULL,
  `image_mobile` text DEFAULT NULL,
  `sound_background` text DEFAULT NULL,
  `active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

LOCK TABLES `story` WRITE;
/*!40000 ALTER TABLE `story` DISABLE KEYS */;

INSERT INTO `story` (`id`, `title`, `description`, `image`, `image_mobile`, `sound_background`, `active`)
VALUES
	(1,'story','story desc',NULL,NULL,NULL,0);

/*!40000 ALTER TABLE `story` ENABLE KEYS */;
UNLOCK TABLES;



/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
