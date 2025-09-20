import agent from 'skywalking-backend-js';

try {
    agent.start({
        serviceName: 'aka-music-frontend',
        serviceInstance: 'aka-music-frontend-instance-0',
        collectorAddress: '127.0.0.1:11800',
        disablePlugins: 'pg/lib/client,mysql/lib/Connection,ioredis,mongoose,express/lib/router,amqplib/lib/channel,mongodb/lib/collection,aws-sdk,mongodb/lib/cursor,mongodb/lib/db',
    });
} catch (error) {
    console.log(error);
}