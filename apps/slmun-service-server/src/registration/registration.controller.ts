import * as common from "@nestjs/common";
import * as swagger from "@nestjs/swagger";
import * as nestAccessControl from "nest-access-control";
import { RegistrationService } from "./registration.service";
import { RegistrationControllerBase } from "./base/registration.controller.base";

@swagger.ApiTags("registrations")
@common.Controller("registrations")
export class RegistrationController extends RegistrationControllerBase {
  constructor(
    protected readonly service: RegistrationService,
    @nestAccessControl.InjectRolesBuilder()
    protected readonly rolesBuilder: nestAccessControl.RolesBuilder
  ) {
    super(service, rolesBuilder);
  }
}
