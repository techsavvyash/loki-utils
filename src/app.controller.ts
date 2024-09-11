import { Controller, Get } from '@nestjs/common';
import { AppService } from './app.service';
import { LokiLogger } from './logger/loki-logger.service';
import { HttpService } from '@nestjs/axios';
import { ConfigService } from '@nestjs/config';

@Controller()
export class AppController {
  constructor(
    private readonly appService: AppService,
    private readonly httpService: HttpService,
    private configService: ConfigService,
    private logger: LokiLogger,
  ) {
    this.logger = new LokiLogger(
      AppController.name,
      httpService,
      configService,
    );
  }

  @Get()
  getHello(): string {
    this.logger.log('Hello World!');
    return this.appService.getHello();
  }
}
