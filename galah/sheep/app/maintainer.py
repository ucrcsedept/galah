# Copyright 2012-2013 John Sullivan
# Copyright 2012-2013 Other contributers as noted in the CONTRIBUTERS file
#
# This file is part of Galah.
#
# Galah is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Galah is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Galah.  If not, see <http://www.gnu.org/licenses/>.

import universal, threading, logging, consumer, producer, time

pollTimeout = 10

_consumerCount = 0
def startConsumer():
    global _consumerCount
    
    consumerThread = threading.Thread(target = consumer.run,
                                      name = "consumer-%d" % _consumerCount)
    consumerThread.start()
    
    _consumerCount += 1
    
    return consumerThread
    
def startProducer():
    producerThread = threading.Thread(target = producer.run, name = "producer")
    producerThread.start()
    
    return producerThread

@universal.handleExiting
def run(znconsumers):
    log = logging.getLogger("galah.sheep.maintainer")
    
    log.info("Maintainer starting")
    
    producer = startProducer()
    consumers = []
    
    # Continually make sure that all of the threads are up until it's time to
    # exit
    while not universal.exiting:
        # Remove any dead consumers from the list
        for c in consumers[:]:
            if not c.isAlive():
                log.warning("Dead consumer detected, restarting")
                
                consumers.remove(c)
        
        # Start up consumers until we have the desired amount
        while len(consumers) < znconsumers:
            consumers.append(startConsumer())
        
        # If the producer died, start it again
        if not producer.isAlive():
            log.warning("Dead producer detected, restarting")
            
            producer = startProducer()
            
        # Sleep for awhile
        time.sleep(pollTimeout)

    raise universal.Exiting()
