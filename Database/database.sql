CREATE DATABASE bd_medicao;

USE bd_medicao;

CREATE TABLE `tb_registro` (
  `id` int NOT NULL AUTO_INCREMENT,
  `temperatura` decimal(10,2) DEFAULT NULL,
  `pressao` decimal(10,2) DEFAULT NULL,
  `altitude` decimal(10,2) DEFAULT NULL,
  `umidade` decimal(10,2) DEFAULT NULL,
  `co2` decimal(10,2) DEFAULT NULL,
  `poeira` decimal(10,2) DEFAULT NULL,
  `tempo_registro` datetime DEFAULT NULL,
  `regiao` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

-- Tabela para o arquivo 'dados_CO.csv'
CREATE TABLE dados_CO (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data_da_coleta DATETIME NOT NULL,
    hora_da_coleta DATETIME NOT NULL,
    medida VARCHAR(255) NOT NULL,
    media_do_horario FLOAT NOT NULL
);

-- Tabela para o arquivo 'dados_poluentes.csv'
CREATE TABLE dados_poluentes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data DATETIME NOT NULL,
    pm25 FLOAT NOT NULL,
    pm10 FLOAT NOT NULL,
    o3 FLOAT NOT NULL,
    no2 FLOAT NOT NULL,
    so2 FLOAT NOT NULL,
    co FLOAT NOT NULL
);

-- Tabela para o arquivo 'dados_temeperatura_SP.csv'
CREATE TABLE dados_temperatura_SP (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATETIME NOT NULL,
    country VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL,
    count INT NOT NULL,
    min FLOAT NOT NULL,
    max FLOAT NOT NULL,
    median FLOAT NOT NULL,
    variance FLOAT NOT NULL
);

-- Tabela para o arquivo 'principais sintomas.csv'
CREATE TABLE principais_sintomas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data_notificacao DATETIME NOT NULL,
    sintomas TEXT NOT NULL
);