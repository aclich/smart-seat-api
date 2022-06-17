--Apply changes to sensor_record

ALTER TABLE `smart_seats`.`sensor_record` 
CHANGE COLUMN `sitting_posture` `sitting_posture` ENUM('regular', 'bias_left', 'bias_right', 'cross_left', 'cross_right', 'stand_on', '1', '2', '3', '4', '5', '6', '7', '8') NULL DEFAULT NULL ;