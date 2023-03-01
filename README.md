# [PoC] PHP Memory Map Visualizer for GDB

This repository contains a Python script for GDB that visualizes the PHP memory map as a color-coded memory map in the GDB TUI (text user interface). The script is useful for debugging memory-related issues in PHP applications and provides a convenient way to visualize the memory usage of a PHP process in real time.

## Introduction

The PHP Memory Map Visualizer for GDB is a powerful tool for PHP developers who need to diagnose and fix memory-related issues in their applications. By providing a visual representation of the PHP memory map, the tool allows developers to quickly identify memory leaks, fragmentation, and other issues that may be affecting application performance.

## Disclaimer

This script is a **proof-of-concept** with extremely limited functionality and should not be used in production environments without thorough testing and modification. The script is provided as-is, without any warranty or support, and the author is not responsible for any damage or data loss that may result from its use. Use at your own risk.

## Installation

To use the PHP Memory Map Visualizer for GDB, you will need to install GDB, PHP with debug symbols, and the dependencies required to build PHP. Here are the basic steps to install the tool:

### Step 1. Clone this repository

``` bash
$ git clone git@github.com:DmitryKirillov/gdb-php-memory.git
```

### Step 2. Install required dependencies

``` bash
$ sudo apt-get install \
    build-essential \
    autoconf \
    automake \
    bison \
    flex \
    re2c \
    libtool \
    make \
    pkgconf \
    git \
    libxml2-dev \
    libsqlite3-dev \
    gdb
```

### Step 3. Install PHP with debug symbols

``` bash
$ git clone https://github.com/php/php-src.git \ 
    --branch=PHP-8.1.14
$ cd php-src
$ ./buildconf --force
$ ./configure \
    --disable-all \
    --enable-cli \
    --enable-debug \
    CFLAGS="-DDEBUG_ZEND=2"
$ make && make test && make install
```

### Step 4. Copy files to the home directory

``` bash
$ cp .gdbinit ~
```

## Usage

To use the PHP Memory Map Visualizer for GDB, you will need to run your PHP script or attach GDB to a running PHP process.

**Running PHP scripts:**

``` bash
$ gdb --args php script.php
```

**Attaching to a running process:**

```
$ ps aux | grep worker.php
root  357167  ... 0:00 php worker.php
$ gdb –p 357167
```

Once GDB is running, you can load and run the PHP Memory Map Visualizer by executing the following commands in the GDB TUI:

``` gdb
(gdb) source php-memory.py
(gdb) layout php-memory
```

## Current Limitations

The PHP Memory Map Visualizer for GDB is a proof-of-concept with several limitations that users should be aware of:

- The tool has only been tested with PHP 8.1.14 and may display unexpected results with other versions of PHP
- The tool works only in CLI mode and may not work with web applications or other types of PHP scripts
- The tool displays only the main chunk of memory (the first 2 Mb) and ignores huge allocations, so it may not provide a complete picture of the memory usage of a PHP process

## Known Issues

Please report any bugs or issues with the PHP Memory Map Visualizer to the project maintainers by opening an issue in the GitHub repository.

## Further Reading

- [The PHP Interpreter](https://github.com/php/php-src)
- [nikic's Blog](https://www.npopov.com/)
- [GDB Documentation](https://sourceware.org/gdb/onlinedocs/gdb/index.html)
