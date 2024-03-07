echo "Preparing examples"
./software/util/buildsite.py -f Examples

echo "Install Ruby dependencies"
bundle install --gemfile=software/scripts/Gemfile --jobs 4 --retry 3

echo "Setup LATEST link"
VER=`./software/util/schemaversion.py`
(cd ./software/site/releases; ln -s "$VER" LATEST)

echo
echo "Run Tests"
(cd software/scripts; bundle exec rake)

echo
echo "Remove LATEST link"
(cd ./software/site/releases; rm LATEST)
