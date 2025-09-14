from django.db import models


class School(models.Model):
    admin_user = models.OneToOneField(
        "accounts.CustomUser", on_delete=models.CASCADE, related_name="school"
    )

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    email = models.EmailField()
    phone = models.CharField(max_length=20)
    website = models.URLField(blank=True, null=True)

    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    map_location_url = models.URLField(blank=True, null=True)

    principal_name = models.CharField(max_length=255, blank=True, null=True)
    established_date = models.DateField(blank=True, null=True)
    registration_number = models.CharField(max_length=100, blank=True, null=True)

    logo = models.ImageField(upload_to="school_logos/", blank=True, null=True)
    banner_image = models.ImageField(upload_to="school_banners/", blank=True, null=True)
    theme_color = models.CharField(max_length=7, blank=True, null=True)  # Hex code

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Grade(models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="classes")
    created_at = models.DateField(auto_now_add=True, null=True)

    class Meta:
        unique_together = ("name", "school")

    def __str__(self):
        return f"{self.name} | {self.school}"

    @staticmethod
    def get_total_fees(grade):
        yearly_fees = grade.fees.filter(fee_type=Fee.FeeType.YEARLY)
        monthly_fees = grade.fees.filter(fee_type=Fee.FeeType.MONTHLY)
        quarterly_fees = grade.fees.filter(fee_type=Fee.FeeType.QUARTERLY)
        bi_monthly_fees = grade.fees.filter(fee_type=Fee.FeeType.BI_MONTHLY)

        lines = [f"Fee Structure for Grade {grade.name}:", "-" * 40]

        # Yearly Fees
        total_yearly = 0
        if yearly_fees.exists():
            lines.append("\nYearly Fees:")
            for fee in yearly_fees:
                lines.append(f"  {fee.name} (YEARLY): Rs. {fee.amount}")
                total_yearly += fee.amount
            lines.append(f"  >> Total Yearly = Rs. {total_yearly}")

        # Monthly Fees
        total_monthly = 0
        if monthly_fees.exists():
            lines.append("\nMonthly Fees:")
            for fee in monthly_fees:
                yearly_equivalent = fee.amount * 12
                lines.append(
                    f"  {fee.name} (MONTHLY): Rs. {fee.amount} x 12 = Rs. {yearly_equivalent}"
                )
                total_monthly += yearly_equivalent
            lines.append(
                f"  >> Total Monthly (Yearly Equivalent) = Rs. {total_monthly}"
            )

        # Quarterly Fees
        total_quarterly = 0
        if quarterly_fees.exists():
            lines.append("\nQuarterly Fees:")
            for fee in quarterly_fees:
                yearly_equivalent = fee.amount * 4
                lines.append(
                    f"  {fee.name} (QUARTERLY): Rs. {fee.amount} x 4 = Rs. {yearly_equivalent}"
                )
                total_quarterly += yearly_equivalent
            lines.append(
                f"  >> Total Quarterly (Yearly Equivalent) = Rs. {total_quarterly}"
            )

        # Bi-Monthly Fees
        total_bi_monthly = 0
        if bi_monthly_fees.exists():
            lines.append("\nBi-Monthly Fees:")
            for fee in bi_monthly_fees:
                yearly_equivalent = fee.amount * 6
                lines.append(
                    f"  {fee.name} (BI-MONTHLY): Rs. {fee.amount} x 6 = Rs. {yearly_equivalent}"
                )
                total_bi_monthly += yearly_equivalent
            lines.append(
                f"  >> Total Bi-Monthly (Yearly Equivalent) = Rs. {total_bi_monthly}"
            )

        grand_total = total_yearly + total_monthly + total_quarterly + total_bi_monthly

        lines.append("\n" + "-" * 40)
        lines.append(f"Grand Total (Yearly Basis): Rs. {grand_total}")

        fee_structure_description = "\n".join(lines)

        return {
            "fee_structure_description": fee_structure_description,
            "grand_total": grand_total,
        }


class Fee(models.Model):
    class FeeType(models.TextChoices):
        MONTHLY = "Monthly", "Monthly"
        YEARLY = "Yearly", "Yearly"
        QUARTERLY = "Quarterly", "Quarterly"
        BI_MONTHLY = "Bi Monthly", "Bi Monthly"

    name = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # eg. 1,00,00,000.00
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="fees")
    fee_type = models.CharField(
        max_length=20, choices=FeeType.choices, default=FeeType.YEARLY
    )

    class Meta:
        unique_together = ("name", "grade")

    def __str__(self):
        return f"{self.name} | {self.grade}"


class TempCSVFile(models.Model):
    file = models.FileField(upload_to="temp_csv_files/")

    def __str__(self):
        return self.file.name

    def delete(self, *args, **kwargs):
        self.file.delete()  # Delete actual file
        super().delete(*args, **kwargs)  # Delete database record
