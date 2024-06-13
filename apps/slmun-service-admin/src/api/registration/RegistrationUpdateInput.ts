import { EventWhereUniqueInput } from "../event/EventWhereUniqueInput";
import { UserWhereUniqueInput } from "../user/UserWhereUniqueInput";

export type RegistrationUpdateInput = {
  event?: EventWhereUniqueInput | null;
  registrationDate?: Date | null;
  user?: UserWhereUniqueInput | null;
};
