up: subst
	docker compose up

down:
	docker compose down --remove-orphans

buildup: subst
	docker compose up --build

detachup:
	docker compose up -d

attach:
	docker compose logs -f

logs:
	docker compose logs

clean:
	docker compose down --rmi local --remove-orphans

prune:
	docker system prune -a --volumes

# export db as a zstd compressed sql file
dumpsql:
	docker compose exec -T db pg_dump -c -U postgres postgres |\
	  zstdmt -19 >postgres.sql.zst

# import db from a zstd compressed sql file
loadsql:
	unzstd -c postgres.sql.zst |\
	  docker compose exec -T db psql -U postgres

# export db as a zstd compressed directory; run only when db stopped
dumpdb:
	sudo tar -cI 'zstdmt -19' -f postgres.tar.zst -C .. postgres
	sudo chown ${USER} postgres.tar.zst

# import db from a zstd compressed directory; run only when db stopped
loaddb:
	sudo chown root postgres.tar.zst
	sudo tar -xI unzstd -f postgres.tar.zst -C .. --recursive-unlink
	sudo chown ${USER} postgres.tar.zst

subst:
	./subst ../angular/src/app/util.service.ts.template >../angular/src/app/util.service.ts
