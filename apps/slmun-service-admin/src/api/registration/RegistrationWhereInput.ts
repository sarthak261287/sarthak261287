import { EventWhereUniqueInput } from "../event/EventWhereUniqueInput";
import { StringFilter } from "../../util/StringFilter";
import { DateTimeNullableFilter } from "../../util/DateTimeNullableFilter";
import { UserWhereUniqueInput } from "../user/UserWhereUniqueInput";

export type RegistrationWhereInput = {
  event?: EventWhereUniqueInput;
  id?: StringFilter;
  registrationDate?: DateTimeNullableFilter;
  user?: UserWhereUniqueInput;
};
