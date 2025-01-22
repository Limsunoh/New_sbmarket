# Generated by Django 4.2 on 2025-01-22 17:05

import django.db.models.deletion
import multiselectfield.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("backend_products", "0001_initial"),
        ("backend_accounts", "0002_alter_user_birth_alter_user_created_at_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Review",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "checklist",
                    multiselectfield.db.fields.MultiSelectField(
                        choices=[
                            ("품질이 우수해요", "품질이 우수해요"),
                            ("합리적인 가격이에요", "합리적인 가격이에요"),
                            ("내구성이 뛰어나요", "내구성이 뛰어나요"),
                            ("친절하고 매너가 좋아요", "친절하고 매너가 좋아요"),
                            ("거래약속을 잘 지켜요", "거래약속을 잘 지켜요"),
                            ("사진과 너무 달라요", "사진과 너무 달라요"),
                            ("돈이 아까워요", "돈이 아까워요"),
                            ("못 쓸 걸 팔았어요", "못 쓸 걸 팔았어요"),
                            ("불친절하게 느껴졌어요", "불친절하게 느껴졌어요"),
                            ("시간을 안 지켜요", "시간을 안 지켜요"),
                        ],
                        max_length=106,
                    ),
                ),
                ("additional_comments", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("score", models.FloatField(default=0)),
                ("is_deleted", models.BooleanField(default=False)),
                ("is_score_assigned", models.BooleanField(default=False)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="backend_accounts.user",
                    ),
                ),
                (
                    "product",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviewed_product",
                        to="backend_products.product",
                    ),
                ),
            ],
        ),
    ]
