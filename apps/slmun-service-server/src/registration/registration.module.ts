import { Module, forwardRef } from "@nestjs/common";
import { AuthModule } from "../auth/auth.module";
import { RegistrationModuleBase } from "./base/registration.module.base";
import { RegistrationService } from "./registration.service";
import { RegistrationController } from "./registration.controller";
import { RegistrationResolver } from "./registration.resolver";

@Module({
  imports: [RegistrationModuleBase, forwardRef(() => AuthModule)],
  controllers: [RegistrationController],
  providers: [RegistrationService, RegistrationResolver],
  exports: [RegistrationService],
})
export class RegistrationModule {}
