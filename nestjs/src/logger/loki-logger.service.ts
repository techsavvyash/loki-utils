import { Logger, LoggerService } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { ConfigService } from '@nestjs/config';
import { catchError, firstValueFrom } from 'rxjs';
import { AxiosError } from 'axios';

export class LokiLogger extends Logger implements LoggerService {
  private readonly httpService: HttpService;
  private readonly configService: ConfigService;

  constructor(
    context: string,
    httpService: HttpService,
    configService: ConfigService,
  ) {
    super(context);
    this.httpService = httpService;
    this.configService = configService;
  }

  /**
   * Function to send a general log, usually for checkpoints and small single line logs without any objects
   * @param message - The message to log
   * @param orgId - The organization ID
   * @param botId - The bot ID
   * @param context - The context of the log
   */
  log(
    message: any,
    orgId: string = 'abc',
    botId: string = 'efg',
    context?: string,
  ) {
    super.log(message, orgId, botId);
    this.pushToLoki('info', message, orgId, botId, context);
  }

  /**
   * Function to log an error message.
   * @param message - The error message to log
   * @param orgId - The organization ID
   * @param botId - The bot ID
   * @param trace - Optional stack trace for the error
   * @param context - The context of the log
   */
  error(
    message: any,
    orgId: string = 'unknown',
    botId: string = 'unknown',
    trace?: string,
    context?: string,
  ) {
    super.error(message, trace, context);
    this.pushToLoki('error', message, orgId, botId, context, trace);
  }

  /**
   * Function to send a warning log.
   * @param message - The warning message to log
   * @param orgId - The organization ID
   * @param botId - The bot ID
   * @param context - The context of the log
   */
  warn(
    message: any,
    orgId: string = 'unknown',
    botId: string = 'unknown',
    context?: string,
  ) {
    super.warn(message, context);
    this.pushToLoki('warn', message, orgId, botId, context);
  }

  /**
   * Function to send a debug log, generally used for detailed debugging information.
   * @param message - The debug message to log
   * @param orgId - The organization ID
   * @param botId - The bot ID
   * @param context - The context of the log
   */
  debug(
    message: any,
    orgId: string = 'unknown',
    botId: string = 'unknown',
    context?: string,
  ) {
    super.debug(message, context);
    this.pushToLoki('debug', message, orgId, botId, context);
  }

  /**
   * Function to send a verbose log, typically for logs that provide more information than a standard log.
   * @param message - The verbose message to log
   * @param orgId - The organization ID
   * @param botId - The bot ID
   * @param context - The context of the log
   */
  verbose(
    message: any,
    orgId: string = 'unknown',
    botId: string = 'unknown',
    context?: string,
  ) {
    super.verbose(message, context);
    this.pushToLoki('verbose', message, orgId, botId, context);
  }

  private async pushToLoki(
    level: string,
    message: any,
    orgId: string,
    botId: string,
    context?: string,
    trace?: string,
  ) {
    const timestamp = Date.now() * 1e6; // Convert to nanoseconds
    const logEntry = {
      level,
      message: typeof message === 'object' ? JSON.stringify(message) : message,
      context: context || this.context,
      trace,
      // You can add more fields here, like orgId and botId if available
    };

    const logs = {
      streams: [
        {
          stream: {
            level,
            env: process.env.NODE_ENV,
          },
          values: [
            [
              timestamp.toString(),
              JSON.stringify(logEntry),
              {
                orgId: orgId,
                botId: botId,
              },
            ],
          ],
        },
      ],
    };
    const LokiURL = this.configService.get<string>('LOKI_INTERNAL_BASE_URL');
    try {
      await firstValueFrom(
        this.httpService
          .post(`${LokiURL}/loki/api/v1/push`, logs, {
            headers: {
              'Content-Type': 'application/json',
            },
          })
          .pipe(
            catchError((error: AxiosError) => {
              console.error(
                'Error pushing logs to Loki:',
                error.response?.data,
              );
              throw error;
            }),
          ),
      );
    } catch (error) {
      console.error('Failed to push logs to Loki:', error);
    }
  }
}
